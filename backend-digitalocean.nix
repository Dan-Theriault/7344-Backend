{
  resources.sshKeyPairs.ssh-key = {};

  monolith = 
    { config, pkgs, ... }:
    {


      deployment.targetEnv = "digitalOcean";
      deployment.digitalOcean.enableIpv6 = true;
      deployment.digitalOcean.region = "nyc3";
      deployment.digitalOcean.size = "s-1vcpu-1gb";
    };
}
