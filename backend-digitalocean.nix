{
  resources.sshKeyPairs.ssh-key = {};

  monolith = { config, pkgs, ... }: {
    deployment = {
      # Other options include AWS, Hetzner, Azure, Google.
      # See NixOps manual for more information
      targetEnv = "digitalOcean";

      digitalOcean = {
        # Regions are listed on DigitalOcean's website
        region = "nyc3";

        # Current size is the basic, $5 / month tier.
        # It has 1GB of memory and 1 virutal cpu.
        # The next most powerful sizes are:
        # s-1vcpu-2gb for $10 / month
        # s-1vcpu-3gb for $15 / month
        # s-2vcpu-2gb for $15 / month
        # s-3vcpu-1gb for $15 / month
        # s-2vcpu-4gb for $20 / month
        # s-4vcpu-8gb for $40 / month
        # Options continue up to a $960 / month offering; 
        # at that point, you're probably better served by a multi-machine architecture.
        size = "s-1vcpu-1gb";
        authToken = builtins.readFile ./secrets/digitalocean.txt;
      };
    };
  };
}
