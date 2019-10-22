#!/bin/bash
set -e # Exit with nonzero exit code if anything fails

sudo apt-get install xmlstarlet

PACKAGE_VERSION=$(xmlstarlet sel -t -m '//VersionPrefix[1]' -v . -n <"Platform.$REPOSITORY_NAME/Platform.$REPOSITORY_NAME.csproj")
PACKAGE_RELEASE_NOTES=$(xmlstarlet sel -t -m '//PackageReleaseNotes[1]' -v . -n <"Platform.$REPOSITORY_NAME/Platform.$REPOSITORY_NAME.csproj")

TAG_ID=$(curl --request GET --url "https://api.github.com/repos/${GITHUB_REPOSITORY}/releases/tags/${PACKAGE_VERSION}" --header "authorization: Bearer ${GITHUB_TOKEN}" | jq -r '.id')

if [ "$TAG_ID" != "null" ]; then
    echo "Release with the same tag already published."
    exit 0
fi

SEPARATOR="

"
PACKAGE_RELEASE_NOTES_STRING=$(jq -saR . <<< "https://www.nuget.org/packages/Platform.$REPOSITORY_NAME/$PACKAGE_VERSION$SEPARATOR$PACKAGE_RELEASE_NOTES")

curl --request POST \
--url "https://api.github.com/repos/$GITHUB_REPOSITORY/releases" \
--header "authorization: Bearer ${GITHUB_TOKEN}" \
--header 'content-type: application/json' \
--data "{
  \"tag_name\": \"${PACKAGE_VERSION}\",
  \"target_commitish\": \"${DEFAULT_BRANCH}\",
  \"name\": \"${PACKAGE_VERSION}\",
  \"body\": $PACKAGE_RELEASE_NOTES_STRING,
  \"draft\": false,
  \"prerelease\": false
  }"
