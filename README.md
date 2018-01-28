# Environmental Sustainability Scorecard - Backend

## Usage

This backend is structured as a RESTful API that receives and sends JSON objects.

*register:*
```
curl https://ess.dtheriault.com/api/register -L -H "Content-Type: application/json" -d
'{"email":"test2","password":"password"}'
```
```
{
  "Status": "User Successfully Registered"
}
```

*login:*
```
curl https://ess.dtheriault.com/api/login -L -H "Content-Type: application/json" -d '{"
email":"test2","password":"password"}'
```
```
{
  "created": "Sun, 28 Jan 2018 06:25:38 GMT",
  "email": "test2",
  "token": "f13727d997239510862167abddb5017f15eb17bfcf60a0a397c0b1d55d2be2f4"
}
```

*logout:*
```
curl https://ess.dtheriault.com/api/logout -L -H "Content-Type: application/json" -d '{
"token": "f13727d997239510862167abddb5017f15eb17bfcf60a0a397c0b1d55d2be2f4"}'
```
```
{
  "Status": "Logged out"
}
```
## Deployment

In the event I am hit by a bus or otherwise incapacitated, you may need to re-deploy this yourselves.

1. Install the nix package manager on a Mac or Linux device.
2. Install NixOps (the deployment tool I used).
3. Add an entry "ssh-config-file" to the NIX_PATH env variable, pointing to a file with contents:
    ```
    Host github.com
      IdentityFile /etc/deploy/id_rsa
      StrictHostKeyChecking=no
    ```
4. Generate an SSH key at /etc/deploy/id_rsa and authorize it as a deployment key on this GitHub Repo
5. Setup a Digital Ocean account, and store an auth token in the environment variable DIGITAL_OCEAN_AUTH_TOKEN
6. Edit backend.nix to use a different domain for dynamic dns (since you don't have my key).
7. `nixops create -d design-prod backend.nix backend-digitalocean.nix`
8. `nixops deploy -d design-prod`

The last step may occasionally fail (automated access to private git repositories is finicky). Re-run once or twice before assuming it's broken. 

An ACME/LetsEncrypt error likely means the deployment host is not publicly reachable.


