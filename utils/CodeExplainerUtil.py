class CodeExplainerUtil:

    @staticmethod
    def create_and_execute_func(func_name, func_args, func_body, args=None):
        """
        Create a function and execute it if args is not None
        :param func_name: function name
        :param func_args: function arguments
        :param func_body: function body
        :param args: arguments, if None, the function will not be executed, just created
        """
        func = 'def ' + func_name + func_args + ':\n\t\t' + func_body
        exec(func)
        if args:
            return locals()[func_name](args)
        else:
            return locals()[func_name]
