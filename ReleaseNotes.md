<img align="right" width="250" height="47" alt="gematik GmbH" src="img/Gematik_Logo_Flag_With_Background.png"/> <br/>

# Release Notes FHIR Publish Tools

## Release 0.3.5

* Set correct title in package feed; should be `<package>#<version>`

## Release 0.3.4

* Fix setting `current` in `package-list.json` if a CI build entry is already present
* More verbose during mirgation
* Remove optional field from ImplementationGuide model

## Release 0.3.3

* Fix handling of publishing of non-first IGs

## Release 0.3.2

* Remove not migrated files
* Added Docker Image

## Release 0.3.1

* Only migrate `.json` and `.html` files

## Release 0.3.0

* Generate `package-list.json` that allows IG Publisher to create comparisons
* Switch from `ig_list.json` to `package-list.json` as history storage

## Release 0.2.1

* Bumped version number for testing

## Release 0.2.0

* Add `version` command to get the tools version
