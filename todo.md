

### Tasks
- [ ] Create levelsv2 ~3d anyone
  - [x] levelsv2 should exists inside database folder
  - [x] levelsv2 should follow similar formats to matching && moderation
  - [x] levelsv2 should use a class to represent levels for easier editing with its own functions
  - [x] wait a few days for testing
  - [ ] should use some sort of server_id that way levels are server-dependant, as it stands they are global
  - [ ] create a new image generator thats nice and pretty for discord levels
- [ ] add functionailty to moderation ~ 4d anyone
  - [ ] Should have a way to set staff roles and staff permissions
  - [ ] moderation should be like wick
  - [ ] roles should have their own permissions
  - [x] moderation should have config for log channels --
  - [ ] moderation should have events that you can opt-into listening
  - [x] moderation should have a mod-logs channel for specifc moderation actions
  - [ ] moderation should have "suspended" role (like quarentine)
  - [ ] moderation should have action specific commands (like create case, but for things like kick/ban/etc etc for ease of use, these will use discords built in permissions)
- [ ] Create a base database obj that has the create, edit, get methods along with self.data and self.doc and self._id datatypes 

```python

# database objects should ingerit this
class basedbobj():
  def __init__(self, data, etc):
    self.data = data
    self.doc = {"_id"..etc}
  
  def edit(self):
    ...
  
  def whatver...
  

```


### Completed Tasks ✓
- [x] None Completed