# from pickletools import optimize
# from google.oauth2 import service_account
# from google.cloud import aiplatform

# import credentials

# myDataset = aiplatform.ImageDataset(credentials.dataset_id)
# print(myDataset.display_name)
# print(myDataset.name)
# print(myDataset.resource_name)

# job = aiplatform.AutoMLImageTrainingJob(
#     display_name="train-example",
#     model_type="CLOUD",
#     multi_label=True,
# )

# model = job.run(
#     dataset=myDataset,
#     training_fraction_split=0.6,
#     validation_fraction_split=0.2,
#     test_fraction_split=0.2,
#     budget_milli_node_hours=8000,
#     model_display_name="test-model",
#     disable_early_stopping=False,
# )

# model.deploy(
#     traffic_percentage=100,
#     endpoint=credentials.endpoint,
#     deployed_model_display_name="Deployed_Model2",
#     min_replica_count=1,
#     max_replica_count=1,
#     sync=True,
# )

# if(credentials.model != None):
#     print("Deleting Model")
#     credentials.model.delete()
#     credentials.model.wait()
# credentials.model = model

# print("___End of algorithm")
