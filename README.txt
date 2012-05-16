This is a multi-part activity that walks through the basics of defining a model.

======
PART 1
======

Define a new model
==================
This is a very easy activity!

In this sample application, there is a new file called models. Inside this file, you can uncomment the lines.

You've now defined a model that specifies an entity type that can be stored to App Engine's Datastore. This model
has a number of properties, all optional, that can be accessed in code and will automatically serialize into the
protocol buffer that is stored in Datastore.

Note that your model is a subclass of ndb.Model. The parent class holds all of the logic for serializing 
and deserializing provides many of the API interfaces for moving data to and from the Datastore.

Also note the way the properties are defined: they appear to be class variables. The ndb.Model class has a metaclass
(a fairly advanced Python concept) that converts these class variables into instance variables when the object
is instantiated. So regardless of how the class definition of an ndb.Model looks, you will still be able to 
access its attributes as expected:

  intro = PlayerModel()
  intro.first_name = 'Jake'
  intro.last_name = 'Cole'
  intro.age = 32

(Don't go past this point until next activity comes up.)

======
PART 2
======

Flesh out your model
====================
In this step, we're going to add some more data to your model. Add the following properties with the most
appropriate data types: biography, email address (required), administrator flag (required, defaults to False). 
Also, add a required property for gender that is limited to the two values 'M' and 'F'. 
Finally, add properties to track when the entity was created and when it was last updated.
