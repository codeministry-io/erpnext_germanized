#!/usr/bin/env bash
# Build the image locally with the same inputs as the CI.
#
#   ./build.sh                          build erpnext_germanized:local for linux/amd64
#   ./build.sh --tag TAG                tag the image as TAG instead
#   ./build.sh --push                   push the image to the registry of TAG instead of loading it
#   ./build.sh --no-cache               build every layer again
#   ./build.sh --platform PLATFORM      build for another platform than linux/amd64
set -euo pipefail

usage() {
	sed -n '4,8s/^#   //p' "$0"
}

value_of() {
	if [[ $# -lt 2 || "$2" == --* ]]; then
		echo "$1 needs a value" >&2
		exit 1
	fi
	printf '%s' "$2"
}

tag="erpnext_germanized:local"
platform="linux/amd64"
output="--load"
no_cache=false

while [[ $# -gt 0 ]]; do
	case "$1" in
	--tag)
		tag=$(value_of "$@")
		shift 2
		;;
	--push)
		output="--push"
		shift
		;;
	--no-cache)
		no_cache=true
		shift
		;;
	--platform)
		platform=$(value_of "$@")
		shift 2
		;;
	-h | --help)
		usage
		exit 0
		;;
	*)
		echo "unknown option: $1" >&2
		usage >&2
		exit 1
		;;
	esac
done

cd "$(dirname "$0")"

python3 -m germanized validate

# BuildKit leaves secrets out of the cache key, so a changed apps.json has to invalidate the bench layer.
cache_bust=$(sha256sum apps.json | cut -c1-16)
# A download of the sources without git history builds as version dev.
version=$(git describe --tags --always --dirty 2>/dev/null || echo dev)

args=(
	--platform "$platform"
	--secret "id=apps_json,src=apps.json"
	--build-arg "CACHE_BUST=$cache_bust"
	--build-arg "VERSION=$version"
	--file Containerfile
	--tag "$tag"
)
if [[ "$no_cache" == true ]]; then
	args+=(--no-cache)
fi

echo "building $tag ($version) for $platform"
docker buildx build "${args[@]}" "$output" .
