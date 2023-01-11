from core.processor import Processor


"""
TODO: 
    load from json,yaml files?
    able to specify chrome properties, etc.
    
"""
class INITIAL_PARAMSProcessor(Processor):
    TPL: str = '{ "key":"value" }'
    DESC: str = f''' 
        - Initial key-value pairs, save to data_chain  

        {TPL}

    '''
    def process(self):
        allParams = self.get_all_params()
        for key in allParams:
            self.populate_data(key, self.expression2str(allParams[key]))
