# lambda-amis-volumes-secrets-deletion

AWS lambda function

# author

Tomer Tcherniak

# Info

```
It has 3 functions:

1. Calculates unused volumes to be deleted (more than 180 days)
2. Calculates secrets to be deleted (from secret manager)
3. Calculates ami's to be deleted ( more than 180 days)
```

# Cloud watch logging

```
For example:
	64f63589-ae98-436b-b3bb-7f411bc4e6a1 *################## Region ############# : eu-west-1 XXXXXXXXXXXX
	64f63589-ae98-436b-b3bb-7f411bc4e6a1 *################## Region ############# : eu-west-1 XXXXXXXXXXXX
	64f63589-ae98-436b-b3bb-7f411bc4e6a1 _# Volumes in eu-west-1 , account id XXXXXXXXXXXX , length volumes to b deleted
	64f63589-ae98-436b-b3bb-7f411bc4e6a1 Deleted Volume in eu-west-1 XXXXXXXXXXXX , VolumeId vol-123456789 , Size 8 , CreateTime 2023-01-07 23:32:00.071000+00:00 
	64f63589-ae98-436b-b3bb-7f411bc4e6a1 Deleted Volume in eu-west-1 XXXXXXXXXXXX , VolumeId vol-987654321 , Size 8 , CreateTime 2023-01-12 06:07:22.500000+00:00 
```
  
  
