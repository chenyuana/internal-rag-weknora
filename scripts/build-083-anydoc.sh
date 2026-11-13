#!/bin/bash
set -euo pipefail
export RUSTUP_HOME=/home/mcdev/weknora083-rustup
export CARGO_HOME=/home/mcdev/weknora083-cargo
export PATH="$CARGO_HOME/bin:/tmp/weknora-go126/go/bin:$PATH"
export CARGO_BUILD_JOBS=2
export RUSTUP_DIST_SERVER=https://rsproxy.cn
export RUSTUP_UPDATE_ROOT=https://rsproxy.cn/rustup
native_root=/home/mcdev/weknora083-anydoc-native
mkdir -p "$native_root/scripts" "$native_root/third_party"
cp /mnt/d/weknora-083-upgrade/scripts/build-anydoc-lib.sh "$native_root/scripts/"
cp -a /mnt/d/weknora-083-upgrade/third_party/anydoc-go "$native_root/third_party/"
cat > "$CARGO_HOME/config.toml" <<'EOF'
[source.crates-io]
replace-with = "rsproxy"
[source.rsproxy]
registry = "sparse+https://rsproxy.cn/index/"
[net]
retry = 2
EOF
bash "$native_root/scripts/build-anydoc-lib.sh"
mkdir -p /mnt/d/weknora-083-upgrade/third_party/anydoc-go/lib/linux_amd64_gnu
cp "$native_root/third_party/anydoc-go/lib/linux_amd64_gnu/libanydoc_go.a" /mnt/d/weknora-083-upgrade/third_party/anydoc-go/lib/linux_amd64_gnu/
