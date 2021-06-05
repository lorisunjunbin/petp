from core.processor import Processor


class CHECK_PARAMProcessor(Processor):
    TPL: str = '{"param_not_empty":"name on data_chain"}'
    DESC: str = f''' 
        - To check the required attribute of data_chain, will terminate the execution or pipeline if given attribute not available.
        {TPL}
    '''

    def process(self):
        paramnames = self.get_param('param_not_empty')
        data = self.get_deep_data(paramnames.split(self.SEPARATOR))

        if data == None or len(data) == 0:
            raise Exception(f'Parameter required: {paramnames} ')
