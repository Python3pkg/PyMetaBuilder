from unittest import TestCase,skip
from PyMetaBuilder import MetaBuilder

class Person(object):
    pass

class PersonMetaBuilder(MetaBuilder.MetaBuilder):

    def __init__(self):
        MetaBuilder.MetaBuilder.__init__(self)
        self.model(Person)
        self.property('name')
        self.property('age',type=int)
        self.property('job',one_of=["doctor", "musician"])
        self.property('height',validates=self.myvalidator)
        self.required('name')

    def myvalidator(self,value):
        pass

class PyMetaBuilderTest(TestCase):

    def setUp(self):
        self.personMeta=PersonMetaBuilder()
        self.personMeta=PersonMetaBuilder()

    def testHierarchy(self):
        self.assertIsInstance(self.personMeta,MetaBuilder.MetaBuilder)

    def testShouldAbleToAddModel(self):
        self.assertEqual(Person,self.personMeta.__getattribute__("_model"))

    def testCheckPropertyset(self):
        self.assertIn('validate_type_age',MetaBuilder.getMethods(self.personMeta))

    def testGetValidatorsName(self):
        val=self.personMeta._getValidatorsByName('age')
        self.assertEqual('validate_type',val[0].__name__)

    def testAttributes(self):
        self.assertTrue('name' in self.personMeta.getProperties())
        self.assertTrue('age' in self.personMeta.getProperties())
        self.assertTrue('job' in self.personMeta.getProperties())
        self.assertTrue('height' in self.personMeta.getProperties())

    def testCorrectAttributeType(self):
        self.personMeta.age=50
        self.assertEqual(50,self.personMeta.age)

    def testIncorrectAttributeType(self):
        def setAge():
            self.personMeta.age='ssse'
        self.assertRaises(TypeError,setAge)

    def testCorrectAttributeOptions(self):
        self.personMeta.job="doctor"
        self.assertEqual("doctor",self.personMeta.job)

    def testIncorrectAttributeOptions(self):
        def setJob():
            self.personMeta.job='ssse'
        self.assertRaises(MetaBuilder.OptionValueError,setJob)

    def testRequiredNotFilled(self):
        def buildWithouthRequired():
            self.personMeta.age=20
            self.personMeta.build()
        self.assertRaises(AttributeError,buildWithouthRequired)

    def test_build(self):
        self.personMeta.age=50
        self.personMeta.name='Jhon Doe'
        instance=self.personMeta.build()
        self.assertIsInstance(instance,Person.__class__)