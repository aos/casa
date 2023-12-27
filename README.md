## casa

Kitty autofeeder scheduler + status

### Development

1. Dev environment: `nix develop`
2. Run locally: `nix run`
3. Build: `nix build`

### Docker image

1. Build with `nix build .#docker`
2. Load to docker: `docker load < result`

Run the image with `--net=host` because we need to be able to discover the
devices on the network.
