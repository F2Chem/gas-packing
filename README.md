# gas-packing
<<<<<<< HEAD
A Django app to faciliate filling cylinders of various sizes as per customer requirements

# Power App
App works by giving you a menu to select what you want to see including: time span, devices, cumulative/difference in readings, interval between readings, and ability to see a graph.
Then takes you to a page that displays a graph with your selections and as many tables as devices selected to display the power meter readings, done using the TimePoint model.

To add a new meter you would need to add it to models.py the same way that they are all already written in, baring in mind the only punctuation allowed is an underscore so meters with 
other punctuation (such as brackets, slashes) must have them swapped out with underscores then the database column specified with its actual name as can be seen used for some already.
Next add the new device to forms.py list DEVICES. First as its name in the database, then with it's user-friendly name for it to be presented as in the UI

If you wanted to add different timespan or interval options, they can be added in views.py by adding to the corresponding dictionaries.
=======
A set of Django apps to faciliate operations at F2 Chemicals Ltd, and ft into an existing Django project.

The first is for filling cylinders of various sizes as per customer requirements, and has the repository is called "gas-packing". See the Wiki for details.
>>>>>>> c377335d70d723331df804b3dfeb851b344dba62
