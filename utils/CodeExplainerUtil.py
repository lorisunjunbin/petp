# Provide a way to execute a given code as string.
# suppose all exec(), evil(), should be in this file in PETP.


class CodeExplainerUtil:

    @staticmethod
    def func_wrapper_call(func_name, func_args, func_body, args):
        func = 'def ' + func_name + func_args + ':\n\t\t' + func_body
        exec(func)
        return locals()[func_name](args)

    @staticmethod
    def func_wrapper(func_name, func_args, func_body):
        func = 'def ' + func_name + func_args + ':\n\t\t' + func_body
        exec(func)
        return locals()[func_name]
