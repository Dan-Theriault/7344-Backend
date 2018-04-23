# Environmental Sustainability Scorecard - Backend

## Usage

This backend is structured as a RESTful API that receives and sends JSON objects.

## Deployment

Our backend code and infrastructure definitions are included in this repository.

Currently, a testing version is deployed on DigitalOcean at ess.dtheriault.com/api. As this version is not intended for production use, it will no longer be available after May 31st, 2018. The deployment process is automated, but you will need to acquire a suitable domain name (we suggest buying one from Namecheap)  and open an account with DigitalOcean, Amazon Web Services, or another hosting provider supported by NixOps.

A configuration for NixOps is included with our backend code. NixOps will handle most of the set-up for the backend application, and enable a number of auxiliary services which make it more performant, secure, and convenient. We define the Server OS configuration in backend.nix, and our cloud infrastructure configuration in backend-digitalOcean.nix. Both files contain extensive comments, explaining required changes (to handle a new domain and host) and present functionality.

After making all required changes, deploy the backend by following the steps below:
1. Install the nix package manager on a Mac or Linux device.
2. Install NixOps by opening a terminal window and run the command “nix-env --install nixops”
3. If you are choosing to use our backend-digitalocean.nix or any other DigitalOcean-hosted configuration, create a DigitalOcean account and follow these instructions to request an auth token, which you’ll use in the next step.
4. Store required secrets as plain text files. Create a subfolder, “secrets” in the same folder as the .nix files. You will need to create three files in this folder; dyndns.txt (containing the dynamic dns password provided by your registrar), digitalocean.txt (containing the auth token from step 3), and ess.txt (containing a 256 character random string).
5. Deploy the configuration by running “nixops create -d design-prod backend.nix backend-digitalocean.nix” and then “nixops deploy -d design-prod”.

You may receive an error originating from the dynamic DNS setup program. This is expected on the initial run, and should resolve itself within a few minutes. If errors persist, the server can be remotely accessed by running “nixops ssh -d design-prod monolith”

If this process is still confusing or cumbersome, please contact our backend developer (Daniel Theriault) for one-time support deploying this backend. You will still need to provide your own domain name and hosting.

