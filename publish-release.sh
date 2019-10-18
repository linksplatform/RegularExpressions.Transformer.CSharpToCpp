#!/bin/bash
set -e # Exit with nonzero exit code if anything fails

# Pull requests and commits to other branches shouldn't try to deploy, just build to verify
if [[ ( "$GITHUB_EVENT_NAME" != "push" ) || ( "$GITHUB_REF" != "$DEFAULT_BRANCH" ) ]]; then
    echo "Skipping release deploy."
    exit 0
fi

sudo apt-get install xmlstarlet jq

PACKAGE_VERSION=$(xmlstarlet sel -t -m '//VersionPrefix[1]' -v . -n <Platform.$REPOSITORY_NAME/Platform.$REPOSITORY_NAME.csproj)
PACKAGE_RELEASE_NOTES=$(xmlstarlet sel -t -m '//PackageReleaseNotes[1]' -v . -n <Platform.$REPOSITORY_NAME/Platform.$REPOSITORY_NAME.csproj)

TAG_ID=$(curl --request GET --url "https://api.github.com/repos/${GITHUB_REPOSITORY}/releases/tags/${PACKAGE_VERSION}" --header "authorization: Bearer ${GITHUB_TOKEN}" | jq -r '.id')

if [ "$TAG_ID" != "null" ]; then
    echo "Release with the same tag already published."
    exit 0
fi

curl --request POST \
--url https://api.github.com/repos/${GITHUB_REPOSITORY}/releases \
--header "authorization: Bearer ${GITHUB_TOKEN}" \
--header 'content-type: application/json' \
--data "{
  \"tag_name\": \"${PACKAGE_VERSION}\",
  \"target_commitish\": \"${DEFAULT_BRANCH}\",
  \"name\": \"${PACKAGE_VERSION}\",
  \"body\": \"${PACKAGE_RELEASE_NOTES}\",
  \"draft\": false,
  \"prerelease\": false
  }"