Pull requests
=============

Pull requests for the `chepy_plugins` repo should follow the following guidelines. 

- Ensure that you follow the docstring format of existing plugins in this repo.
- Without proper docstrings, Chepy cli will not provide autocompletion. 
- Plugin methods for this repo should return `ChepyPlugin` in its return docstring. This helps differentiate between core methods and plugin methods. 
- Follow good method naming convention. Try to avoid namespace collisions. 