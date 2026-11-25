# dotnix

My NixOS config. The private parts (secrets, network drives, private DNS)
live in a separate repo that builds on this one.

```bash
nix develop
just switch     # build this machine and switch
just build      # build and show what changes
just check      # evaluate every host, run the checks
just update     # update inputs
just iso        # build the live system and installer
```

## Layout

```
flake.nix           inputs only
modules/
  flake/            outputs, lib (mkHost), checks
  generic/          every class: dotnix.* options, nix (lix, caches), home-manager
  nixos/ wsl/ iso/ darwin/
                    one per class; each imports generic/
  home/             home-manager modules
  profiles/         my bundles of settings, turned on per host
  hardware/         drop-in hardware modules
  wm/               window managers, drop-in modules
packages/           scripts (bin/), c-tools (src/), dotnix-install
hosts/<name>/       one folder per machine
home/<user>/        one folder per user
old/                the previous config, until it is ported
```

## Hosts

A machine is `hosts/<name>/default.nix` plus one line in
`modules/flake/default.nix`:

```nix
nixosConfigurations = mkHosts {
  kazuha = { };
  <name> = { };                        # x86_64 nixos
  <name> = { arch = "aarch64"; };
  <name> = { class = "iso"; };
  <name> = { class = "wsl"; };         # needs the nixos-wsl input
};

darwinConfigurations = mkHosts {
  <name> = { arch = "aarch64"; class = "darwin"; };   # needs the darwin input
};
```

`mkHost` loads `hosts/<name>` and `modules/<class>`, and sets the host
name and platform. For a new machine, generate its hardware file on it:

```bash
nixos-generate-config --show-hardware-config > hosts/<name>/hardware.nix
```

## Live system

`just iso` builds `result/iso/*.iso`: my desktop, shell, editors and theme
on any machine, logged in as me. Write it to a stick with
`dd if=result/iso/*.iso of=/dev/sdX bs=4M status=progress`.

On it, mount the target at `/mnt` and run `dotnix-install`. It installs
one of the machines in `hosts/`, sets up a new one (a host folder, its
hardware file and a line in the host list), or plain NixOS. The config
ends up in `~/dotnix` on the new machine; commit the new host from there.

## Drop-in modules

Modules under `modules/wm/` (more to come) only read their own
`dotnix.<name>` options, so they work in any config:

```nix
imports = [ inputs.dotnix.nixosModules.niri ];
dotnix.niri.enable = true;
```

`nix flake check` evaluates each one alone to keep it that way.

## New machines

For a machine that is not mine or not on NixOS yet. Every command works in
fish and bash.

Install Nix (Lix, with flakes on):

```bash
curl -sSf -L https://install.lix.systems/lix | sh -s -- install
```

Try my editor or scripts without installing them:

```bash
nix run github:pandecode/hermes --extra-experimental-features 'nix-command flakes' --accept-flake-config
nix shell github:pandecode/dotnix#scripts --extra-experimental-features 'nix-command flakes'
```

tmux:

```bash
curl -fsSL https://raw.githubusercontent.com/pandecode/dotnix/main/config/tmux/.tmux.conf -o ~/.tmux.conf
```

Join the tailnet, then trust the home CA and use firefly's cache. The
`*.home.arpa` names resolve over tailscale only.

```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
curl -fsSL https://raw.githubusercontent.com/pandecode/dotnix/main/keys/home-ca.crt -o /tmp/home-ca.crt
sudo cp /tmp/home-ca.crt /usr/local/share/ca-certificates/home-ca.crt && sudo update-ca-certificates   # debian, ubuntu
sudo trust anchor --store /tmp/home-ca.crt                                                              # fedora, arch
printf 'extra-substituters = https://cache.home.arpa\nextra-trusted-public-keys = cache.home.arpa-1:MGX9S25yklvCd6fGThto3O9wfHw7AHr5JeKE/fFb7PA=\nconnect-timeout = 5\n' | sudo tee -a /etc/nix/nix.conf
sudo systemctl restart nix-daemon
```

The cache key is `keys/nix-cache`; change it here too if that file changes.

Give me access:

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh && curl -fsSL https://raw.githubusercontent.com/pandecode/dotnix/main/keys/kazuha.pub >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys
```

Take it away again:

```bash
curl -fsSL https://raw.githubusercontent.com/pandecode/dotnix/main/keys/kazuha.pub | grep -vxFf - ~/.ssh/authorized_keys > ~/.ssh/authorized_keys.new; mv ~/.ssh/authorized_keys.new ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys
```
