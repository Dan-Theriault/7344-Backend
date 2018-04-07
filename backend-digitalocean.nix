{
  resources.sshKeyPairs.ssh-key = {};

  monolith = 
    { config, pkgs, ... }:
    {
      # Other options include AWS, Hetzner, Azure, Google.
      deployment.targetEnv = "digitalOcean";
      deployment.digitalOcean.region = "nyc3";
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
      deployment.digitalOcean.size = "s-1vcpu-1gb";
    };
}
