# Changelog

## Version 9.0.0 - 2023-06-01

- Added optional keyword argument `preprocess_config` to `create_prediction`
- Removed optional keyword argument `auto_rotate` from `create_prediction`, use `preprocess_config` instead
- Removed optional keyword argument `image_quality` from `create_prediction`, use `preprocess_config` instead
- Removed optional keyword argument `max_pages` from `create_prediction`, use `preprocess_config` instead
- Removed optional keyword argument `rotation` from `create_prediction`, use `preprocess_config` instead
- Added optional keyword argument `data_scientist_assistance` to `create_training`
- Removed optional keyword argument `instance_type` from `create_training`

## Version 8.10.0 - 2023-04-18

- Added `get_deployment_environment`
- Added `list_deployment_environments`

## Version 8.8.0 - 2023-02-23

- Added optional keyword argument `rotation` to `create_prediction`

## Version 8.7.0 - 2023-01-30

- Added optional keyword argument `base_model` to `create_model`
- Added optional keyword argument `owner` to `list_models`

## Version 8.6.0 - 2022-09-27

- Added optional keyword argument `cpu` to `update_transition`
- Added optional keyword argument `image_url` to `update_transition`
- Added optional keyword argument `memory` to `update_transition`
- Added optional keyword argument `secret_id` to `update_transition`
- Added optional keyword argument `from_start_time` to `list_workflow_executions`
- Added optional keyword argument `to_start_time` to `list_workflow_executions`

## Version 8.4.0 - 2022-05-23

- Added optional `postprocess_config` to `create_model`
- Added optional `postprocess_config` to `update_model`

## Version 8.3.0 - 2022-05-09

- Moved optional `training_id` in `update_model` to `optional_args`

## Version 8.2.0 - 2022-04-22

- Added `create_payment_method`
- Added `delete_payment_method`
- Added `get_payment_method`
- Added `list_payment_methods`
- Added `update_payment_method`
- Added optional `payment_method_id` to `update_organization`

## Version 8.1.0 - 2022-04-12

- Added optional keyword argument `sort_by` to `list_documents`
- Added optional keyword argument `order` to `list_documents`
- Added optional keyword argument `sort_by` to `list_predictions`
- Added optional keyword argument `order` to `list_predictions`

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
