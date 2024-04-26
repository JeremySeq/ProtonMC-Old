# ProtonMC

A website control panel for Minecraft servers. Made with Python Flask.

## Raspberry Pi Changes:

- Raspberry Pi gives a ConnectionRefusedError in isOn() in mc.py, add exception for it and return false
- in servers.json, the slashes are just "/" instead of "\\" used for windows


### run.sh
- in the server folder run.bat must be changed to run.sh because linux does not have batch files
- run.sh should look like this:
```
#!/usr/bin/env bash
cd /home/jeremyseq/Documents/ProtonMC/servers/TestServer; java -Xmx3G -Xms3G -jar server.jar nogui
```



- in startServer() function in mc.py, run.bat must be changed run.sh

- in startServer() function in mc.py, the subprocess must be created differently because it uses a bash script instead of batch:
`s = subprocess.Popen(["/bin/bash", serverRunPath], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)`

## User Accounts
- user accounts are created in `users.json` file
- example of `user.json` file:

    ```json
    {
        "admin": {
            "username": "admin",
            "password": "password",
            "permissions": 5
        },

        "example_user": {
            "username": "example_user",
            "password": "example_user_password",
            "permissions": 3
        }
    }
    ```
- each user account has a permission level that determines access to certain actions, see [Permissions](#permissions)


## Security Related Features
- see [Permissions](#permissions)
- see [User Accounts](#user-accounts)
- Some properties are not shown in the options tab:
    1. RCON Password
    2. RCON Port
    3. Query Port
    4. Server IP


## Permissions
Permission Levels are from 1 - 5

| Action                | Minimum Permission Level Required |
| --------------------- | --------------------------------- |
| Restore Backup        | 5                                 |
| Send Commands         | 4                                 |
| Change Options        | 4                                 |
| View Options Page     | 3                                 |
