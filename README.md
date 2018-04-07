# Environmental Sustainability Scorecard - Backend

## Usage

This backend is structured as a RESTful API that receives and sends JSON objects.

## Deployment

Currently, the backend is deployed on the smallest available DigitalOcean droplet tier.
This droplet is sized for testing purposes only,
and will no longer be available after May 31st.


There are two possible approaches for a production deployment.
First, you could simply take the Flask application we developed and arrange your own architecture.
Some environment variables must be set for the application to function.
`ESS_DATABASE_URI` must be the URI for a valid PostgreSQL database to which the user running our app has full access.
`ESS_SECRET` should be a 256 character random string; it is used as the secret salt for authentication tokens.

Second, you can use the NixOps automated deployment configuration included in this repository.
This automated configuration will set up the backend application, 
as well as a number of services which make it more performant, secure, and convenient.
We define the Server OS configuration in `backend.nix`,
and our cloud infrastructure configuration in `backend-digitalOcean.nix`.
Together, these two configuration files define our total infrastructure.

The values of some fields do need to be changed;
for instance, the server will currently attempt to use our testing domain name.
As this domain is not specific to this project,
we are not providing credentials for its use -- you will need to acquire a domain name for this project.
Please read the comments in `backend.nix` for more information.

After making any needed changes, you can deploy this configuration by following these instructions:

1. Install [the nix package manager](https://nixos.org/nix/) on a Mac or Linux device.
2. Using nix, install NixOps; `nix-env --install nixops`
3. If you are choosing to use our `backend-digitalocean.nix` or any other DigitalOcean-hosted configuration, [create a DigitalOcean account](https://www.digitalocean.com) and [follow these instructions to request an auth token](https://www.digitalocean.com/community/tutorials/how-to-use-the-digitalocean-api-v2). Store the token in the environment variable `DIGITAL_OCEAN_AUTH_TOKEN`.
4. Deploy the configuration by running `nixops create -d design-prod backend.nix backend-digitalocean.nix` and then `nixops deploy -d design-prod`.

Please also note that:
- A test suite against the API is included in our mobile application's code. If the server deployed successfully, all tests should pass.
- You can remotely access this server (from the machine you deployed from) by running `nixops ssh -d design-prod monolith`.



