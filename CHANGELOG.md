# Changelog

## Version 8.1.0 - 2022-04-12

- Added `sort_by` to `list_documents`
- Added `order` to `list_documents`
- Added `sort_by` to `list_predictions`
- Added `order` to `list_predictions`

## Version 8.0.0 - 2022-03-15

- width and height is now optional in create_model

## Version 7.1.0 - 2022-03-04

- Added training_id to create_prediction
- Added training_id to update_model

## Version 7.0.0 - 2022-02-23

- Removed positional argument status from update training (Breaking change)

## Version 6.0.0 - 2022-02-18

- Added metadata to create_document, update_document, create_dataset, update_dataset, create_model, update_model and create_training
- Fixed tests after recursive groundTruthList in Open API Spec
- Added update_training
- Removed status from update_model (Breaking change)
- Remove member variable endpoint from Client, use credentials.api_endpoint instead (Breaking change)

## Version 5.2.0 - 2021-11-29

- Added get_plan
- Added list_plans
- Added create_training
- Added list_trainings

## Version 5.1.1 - 2021-11-10

- Added Exception classes for BadRequest and NotFound

## Version 5.1.0 - 2021-11-05

- Added optional keyword argument postprocess_config to create_prediction

## Version 5.0.0 - 2021-10-13

- Removed all support for batches. Use datasets instead.

## Version 4.0.0 - 2021-09-10

- Added get_dataset
- Remove API key from credentials

### Breaking changes

- Credentials no longer use the api_key to access the API.

## Version 3.5.0 - 2021-09-06

- Added support for caching tokens. Specify use_cache = True in credentials.cfg to turn on caching. Defaults to false

## Version 3.4.1 - 2021-08-31

- Argument content_type is now optional for create_document
- warning will be given if the guessed and the provided content type does not match

## Version 3.4.0 - 2021-06-29

- Added delete_document
- Added create_dataset
- Added list_datasets
- Added update_dataset
- Added delete_dataset
- Added optional parameter dataset_id to create_document
- Added optional parameter dataset_id to list_documents
- Added optional parameter dataset_id to delete_documents
- Added optional parameter dataset_id to update_document
- Added parameter delete_all to delete_documents
- Added create_data_bundle
- Added list_data_bundles
- Added update_data_bundle
- Added delete_data_bundle

## Version 3.3.1 - 2021-06-18

- Updated logger to show more meta information
- Fixed bug causing two log messages to be printed

## Version 3.3.0 - 2021-06-16

- Added get_organization
- Added update_organization

## Version 3.2.15 - 2021-05-27

- Added delete_model

## Version 3.2.14 - 2021-05-25

- Added login_urls and default_login_url to create_app_client

## Version 3.2.13 - 2021-05-11

- Added create_model
- Added update_model
- Added get_model
- Added update_batch
- Added update_app_client

## Version 3.2.12 - 2021-05-10

- Added argument app_client_id to create_user
