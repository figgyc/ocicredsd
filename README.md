# ocicredsd
**PERSONAL PROJECT, IN DEVELOPMENT, NOT SECURITY AUDITED** or official or anything! No guarantee of security, don't use for anything critically important.

`ocicredsd` is a small helper that bridges [systemd credentials](https://www.freedesktop.org/software/systemd/man/latest/systemd.exec.html#Credentials) with [Oracle Cloud Infrastructure Vault](https://docs.oracle.com/en-us/iaas/Content/KeyManagement/home.htm), using systemd's support for `AF_UNIX` credential providers. 

## Example
Once you have configured a dynamic group with the right permissions for your OCI instance (eg [like this](https://www.ateam-oracle.com/post/using-the-oci-instance-principals-and-vault-with-python-to-retrieve-a-secret)) and started `ocicredsd` you can access your credentials like this in `.service` units:

```ini
[Service]
Type=oneshot
ExecStart=/usr/bin/cat %d/some-password
# Or:
ExecStart=/usr/bin/cat ${CREDENTIALS_DIRECTORY}/some-password
LoadCredential=some-password:/run/ocicredsd/ocicredsd.sock
```

Or in Podman Quadlet `.container` units. Note that %d expansion only works in `Exec` lines, so `EnvironmentFile` in regular `.service` units cannot be a credential, you would have to use an ExecStartPre script to load the variables.
```ini
[Container]
Image=docker.io/alpine
Exec=env
EnvironmentFile=%d/some-env

[Service]
LoadCredential=some-env:/run/ocicredsd/ocicredsd.sock

```


## Installation
ocicredsd requires Python 3 with the `oci` SDK package. Or use the container. Set the `OCI_VAULT_ID` environment variable to the ID of your vault (only one vault is supported currently, you could use multiple instances to work around this). Set `SOCKET_PATH` as appropriate. If not running in a container you could also use systemd socket activation.