import paramiko
import argparse
from common.log import logger
from pathlib import Path
import re
from typing import Dict, List
import os
import time


class JumpServerClient:
    RETURN_NEWLINE_CHACATER = "\r\n"
    LOGIN_TERMINAL_END_FLAG = "$"

    def __init__(self, user: str, jump_server_host: str, jump_server_port: int,
                 target_host: str, password: str = None, private_key_file: str = None):
        self.__ssh_client = paramiko.SSHClient()
        # 处理 SSH 连接中未知主机密钥的策略类, 可以自动添加新的主机密钥而不需要人工干预
        self.__ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
        self.__user = user
        self.__target_host = target_host
        self.__jump_server_host = jump_server_host
        self.__jump_server_port = jump_server_port
        self.__ssh_channel = None
        if password is None:
            self.__use_private_key = True
            self.__private_key_file = private_key_file
        else:
            self.__use_private_key = False
            self.__password = password

    def connect(self):
        try:
            if self.__use_private_key:
                # 使用私钥免密登陆 jumpserver 堡垒机
                if self.__private_key_file is None:
                    # 使用 look_for_keys 从 ~/.ssh 下搜索私钥
                    self.__ssh_client.connect(
                        hostname=self.__jump_server_host,
                        port=self.__jump_server_port,
                        username=self.__user,
                        allow_agent=False,
                        look_for_keys=True,  # 自动寻找私钥
                        disabled_algorithms={'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}
                    )
                else:
                    # 使用指定的私钥文件
                    self.__ssh_client.connect(
                        hostname=self.__jump_server_host,
                        port=self.__jump_server_port,
                        username=self.__user,
                        allow_agent=False,
                        key_filename=self.__private_key_file,
                        disabled_algorithms={'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}
                    )
            else:
                # 使用密码登陆
                self.__ssh_client.connect(
                    hostname=self.__jump_server_host,
                    port=self.__jump_server_port,
                    username=self.__user,
                    password=self.__password,
                    allow_agent=False,  # 禁用 SSH 代理, 禁用后不会尝试使用系统上运行的 SSH 代理来获取密钥, 需要明确提供密钥
                    look_for_keys=False,  # 禁止在用户的 ~/.ssh 目录下查找私钥文件
                )
            self.__ssh_channel = self.__ssh_client.invoke_shell()
            # 设置读写超时时间为 2 秒
            self.__ssh_channel.settimeout(2)
        except Exception as e:
            self.close()
            return False, repr(e)
        logger.info(f'connect to jump-server [{self.__jump_server_host}] successfully!')
        return True, ""

    def exec_block(self, command: str):
        start_time = time.time()
        # 阻塞式执行命令，直到返回数据
        # self.__send_command(command)
        self.__ssh_channel.send(command + '\n')
        is_success, output = self.__recv()
        # 统计耗时
        end_time = time.time()
        elapsed_time = end_time - start_time
        logger.info(f'exec cmd [{command}] cost [{elapsed_time}] seconds, output [\n{output}\n]')
        if not is_success:
            logger.error(f'exec cmd [{command}] fail with err [{output}]')
            return False, output
        # 剔除转义字符和颜色
        output = self.__beautify_output(output)
        # 返回的内容会带上输入的命令, 需要移除一下
        output = output.replace(command, '', 1)
        return True, output

    def __beautify_output(self, output: str, clear_color=True):
        # 剔除转义字符
        character_to_remove = [
            '\x1b[H',  # 将光标移动到屏幕的左上角
            '\x1b[2J',  # 清除屏幕上的所有内容
        ]
        for char in character_to_remove:
            output = output.replace(char, '')
        # 剔除颜色
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        output = ansi_escape.sub('', output)
        return output

    def __wait_for_output(self, output: str):
        # 等待交互式终端出现指定的字符
        stdout = ''
        while stdout.find(output) == -1:
            try:
                stdout += self.__ssh_channel.recv(65535).decode('utf-8')
            except Exception as e:
                logger.error(f'wait for output [{output}] fail with err [{repr(e)}]')
                logger.error(f'current output [{stdout}]')
                return False, repr(e)
        logger.info(f'beautify content\n{self.__beautify_output(stdout)}')
        return True, ""

    def __send_command(self, input: str):
        self.__ssh_channel.send(input)
        self.__ssh_channel.send(self.RETURN_NEWLINE_CHACATER)

    def __recv(self):
        # 从终端接收数据, 接收成功后末尾是终端提示符 LOGIN_TERMINAL_END_FLAG
        stdout = ''
        while not (stdout.rstrip().endswith(self.LOGIN_TERMINAL_END_FLAG)):
            try:
                stdout += self.__ssh_channel.recv(65535).decode('utf-8')
            except Exception as e:
                logger.error(f'read data from channel fail with err [{repr(e)}]')
                logger.error(f'current stdout:\n{stdout}')
                return False, repr(e)
        logger.info(f'read output from terminal successfully!\n{stdout}')
        return True, stdout

    def login(self, login_target_host_prompt: str, prompt2input: List[Dict[str, str]] = None):
        # 实现交互式登录 target_host
        # @param login_target_host_prompt: 登陆 target_host 提示词
        # @param prompt2input: 提示词, 例如 [{'Please enter your ID':'tomocat'}, {'Please enter your password': 'my_password'}, {'select your user for login':'1'}]

        # 先处理前置 prompt 实现交互式登录W
        if not prompt2input is None:
            for elem in prompt2input:
                prompt, input = list(elem.items())[0]
                is_success, errmsg = self.__wait_for_output(prompt)
                if not is_success:
                    logger.error(f'wait for prompt [{prompt}] fail with err [{errmsg}]')
                    return False, errmsg
                self.__send_command(input)
        # 登陆 target_host
        is_success, errmsg = self.__wait_for_output(login_target_host_prompt)
        if not is_success:
            logger.error(f'wait for login-prompt fail with err [{errmsg}]')
            return False, errmsg
        self.__send_command(f'{self.__target_host}')
        is_success, output = self.__recv()
        if not is_success:
            logger.error(f'login fail with err [{errmsg}]')
            return False, output
        logger.info(f'login to target host [{self.__target_host}] successfully with output:\n{output}')

    def close(self):
        if not self.__ssh_channel is None:
            self.__ssh_channel.close()
            self.__ssh_channel = None
        if not self.__ssh_client is None:
            self.__ssh_client.close()
            self.__ssh_client = None


# Reference:
# https://www.cnblogs.com/shouke/p/10157487.html
#
# 调试脚本:
# python3 -m client.jump_ssh_client --user tomocat --password my_password --jump_host 192.168.1.1 --target_host 192.168.1.2
"""
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='test for ssh-client'
    )
    parser.add_argument('--user', type=str, required=True, help='user name')
    parser.add_argument('--password', type=str, required=True, help='password')
    parser.add_argument('--jump_host', type=str, required=True, help='jump server hostname')
    parser.add_argument('--target_host', type=str, required=True, help='target hostname')
    global GLOBAL_ARGS
    GLOBAL_ARGS = parser.parse_args()
    logger.info(f'args: [{GLOBAL_ARGS}]')

    # 构造堡垒机 ssh client
    start_time = time.time()
    client = paramiko.SSHClient()
    # 处理 SSH 连接中未知主机密钥的策略类, 可以自动添加新的主机密钥而不需要人工干预
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    # TODO: 使用 private_key 而非密钥连接
    # client.connect(
    #     hostname=GLOBAL_ARGS.jump_host,
    #     port=2222,
    #     username=GLOBAL_ARGS.user,
    #     # key_filename=os.path.join(Path.home(), '.ssh/id_rsa'),
    #     look_for_keys=True,  # 自动寻找密钥
    #     allow_agent=False,
    #     disabled_algorithms={'pubkeys': ['rsa-sha2-256', 'rsa-sha2-512']}
    # )
    client.connect(
        hostname=GLOBAL_ARGS.jump_host,
        port=2222,
        username=GLOBAL_ARGS.user,
        password=GLOBAL_ARGS.password,
        allow_agent=False,  # 禁用 SSH 代理, 禁用后不会尝试使用系统上运行的 SSH 代理来获取密钥, 需要明确提供密钥
        look_for_keys=False,  # 禁止在用户的 ~/.ssh 目录下查找私钥文件
    )
    logger.info(f'successfully connect to jump-server [{GLOBAL_ARGS.jump_host}]')
    channel = client.invoke_shell()
    # 设置读写超时时间为 2 秒
    channel.settimeout(2)

    # 尝试读取到 'Opt>' 数据
    stdout = ''
    while stdout.find('Opt>') == -1:
        try:
            stdout += channel.recv(65535).decode('utf-8')
        except Exception as e:
            logger.error(f'read content from jump-server [{GLOBAL_ARGS.jump_host}] fail')
            exit(-1)
        time.sleep(0.1)
    # 打印原始的数据
    # logger.info(f'read content from jump-server successfully!\n{stdout}')
    # 打印可视化字符 (方便 debug)
    # logger.info(f'repr content\n{repr(stdout)}')

    def beautify_str(content: str):
        # 剔除转义字符
        character_to_remove = [
            '\x1b[H',  # 将光标移动到屏幕的左上角
            '\x1b[2J',  # 清除屏幕上的所有内容
        ]
        for char in character_to_remove:
            content = content.replace(char, '')
        return content
    # 打印剔除转义后的字符
    logger.info(f'beautify content\n{beautify_str(stdout)}')

    # 登陆到对应的目标机器 (登录提示符 ~$)
    channel.send(f'{GLOBAL_ARGS.target_host}\r\n')
    login_end_chacater = '$'
    stdout = ''
    while not (stdout.rstrip().endswith(login_end_chacater)):
        try:
            stdout += channel.recv(65535).decode('utf-8')
        except Exception as e:
            logger.error(f'read data from channel fail with err [{repr(e)}]')
            logger.error(f'stdout:\n{stdout}')
            exit(-1)
    logger.info(f'read output\n{stdout}')

    # 在目标机器上输出指令获取输出
    channel.send(f'tree ~/firmware')
    channel.send(f'\r\n')
    stdout = ''
    while not (stdout.rstrip().endswith(login_end_chacater)):
        try:
            stdout += channel.recv(65535).decode('utf-8')
        except Exception as e:
            logger.error(f'read data from channel fail with err [{repr(e)}]')
            logger.error(f'stdout:\n{stdout}')
            exit(-1)
    logger.info(f'read outout\n{stdout}')

    # 统计耗时
    end_time = time.time()
    elapsed_time = end_time - start_time
    logger.info(f'time cost: {elapsed_time} seconds')

    # 需要主动关闭, 否则下次可能登录不上
    channel.close()
"""

# 调试脚本:
# python3 -m client.jump_ssh_client --user tomocat --password my_password
if __name__ == '__main__':
    print('---------------------------- JumpSshClient ----------------------------')
    # 配置命令行参数
    parser = argparse.ArgumentParser(
        description='test for JumpServerClient'
    )
    parser.add_argument('--user', type=str, required=True, help='user name')
    parser.add_argument('--password', type=str, required=True, help='password')
    parser.add_argument('--jump_host', type=str, required=True, help='jump server hostname')
    parser.add_argument('--target_host', type=str, required=True, help='target hostname')
    global GLOBAL_ARGS
    GLOBAL_ARGS = parser.parse_args()
    logger.info(f'args: [{GLOBAL_ARGS}]')

    # 注册 JumpServerClient
    client = JumpServerClient(user=GLOBAL_ARGS.user, jump_server_host=GLOBAL_ARGS.jump_host,
                              jump_server_port=2222, password=GLOBAL_ARGS.password, target_host=GLOBAL_ARGS.target_host)
    is_success, errmsg = client.connect()
    if not is_success:
        logger.info(f'connect fail with errmsg [{errmsg}]')
        exit(-1)
    logger.info('connect successfully!')
    client.login(login_target_host_prompt='[Host]>', prompt2input=[{"Opt>": "Data"}])
    is_success, output = client.exec_block('tree ~/firmware')
    if is_success:
        logger.info(f'exec cmd success with output [{output}]')
    client.close()
    print('---------------------------- JumpSshClient ----------------------------')
