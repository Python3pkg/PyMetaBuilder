import types

def getMethodsByName(obj,name):
    return [method for method in getMethods(obj) if name in method]

def getMethods(obj):
    return [e for e in dir(obj) if callable(getattr(obj, e))]

def getAttributes(obj):
    return [prop for (prop,value) in vars(obj).iteritems()]

def createvar_if_not_exists(obj, var, initial):
    try:
        getattr(obj,var)
    except AttributeError:
        setattr(obj, var, initial)

class MetaBuilder():

    def __init__(self):
        self.prefix = 'validate_'
        self.validators = self._get_Validators()
        self.callbacks = dict()
        for v in self.validators:
            self.callbacks[v.split(self.prefix)[1]]=getattr(self,v)

    #Validators
    def _get_Validators(self):
        return getMethodsByName(self, self.prefix)

    def _getValidatorsByName(self,name):
        return [getattr(self,val) for val in self._get_Validators() if name in val]

    def validate_type (self,value,expected_type):
        if not type(value) in ([expected_type] + expected_type.__subclasses__()):
            raise TypeError,"Should be of type %s" % expected_type

    def validate_one_of(self,value,options):
        if value not in options:
            raise OptionValueError,"Value %s not in expected options" % value

    def validate_validates(self,value,method):
        return self.customMethodValidator(value,method)

    def customMethodValidator(self,value,method):
        if not callable(method):
            raise TypeError,"%s is not a method or callable one" % method
        try:
            if not method(value):
                raise ValidatorError,"Value %s did not passed validation %s"  % (value,method)
        except TypeError,e:
            raise ValidatorError,e,'Problem calling method %s' % method

    def required(self,*args,**kwargs):
        self._required_args=[]
        for arg in args:
            self._required_args.append(arg)

    def model(self,klass):
        createvar_if_not_exists(self,"_model",klass)
        self._model=klass

    def property(self,attribute,*args,**kwargs):
        """
        self.property('age',type=int)
        """
        callback=self.getCallback(*args,**kwargs)
        if callback:
            callbackName=callback.__name__+'_'+attribute
            self.__dict__[callbackName]=types.MethodType(callback,self)
        #create setter and getters
        self.buildProperty(attribute,callbackName)

    def buildProperty(self,attributeName,callbackName=None):
        self.buildGetter(attributeName)
        self.buildSetter(attributeName,callbackName)

    def buildGetter(self,propertyName):
        setter="def set{0}(self):" \
               "    return _{1}".format(propertyName,self._getAttrName(propertyName))
        self.createFunction(self.__class__,"get{0}".format(propertyName),setter)

    def buildSetter(self,propertyName,callbackName):
        getter="def set{0}(self,value):" \
               "    {1}(value)" \
               "    _{2}=value".format(propertyName,callbackName,self._getAttrName(propertyName))#Armar un CodeType antes de armar el FunctionType
        self.createFunction(self.__class__,"get{0}".format(propertyName),getter)

    def createFunction(self,klass,methodName,code):
        d = {}
        exec code.strip() in d
        setattr(klass,methodName, d[methodName])

    def getCallback(self,*args,**kwargs):
        for kwarg,validateArg in kwargs.iteritems():
            for callbackname,callback in self.callbacks.iteritems():
                if callbackname==kwarg:
                    return callback
            return None

class OptionValueError(StandardError):
    def __init__(self, *args, **kwargs):
        StandardError.__init__(self, *args, **kwargs)

class ValidatorError(StandardError):
    def __init__(self, *args, **kwargs):
        StandardError.__init__(self, *args, **kwargs)

class MyBuilder(MetaBuilder):
    pass

if __name__ == '__main__':
    a=MyBuilder()
    a.property('bleh',type=int)


