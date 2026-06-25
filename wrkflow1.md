# Workflow 1 Implementation Plan



## Garment Template Creation Service



### Version 1.0 (CPU-Only MVP)



---



# 1. Implementation Objectives



Build a service capable of:



1. Accepting garment image uploads.

2. Validating image quality.

3. Removing image backgrounds.

4. Generating garment masks.

5. Extracting garment metadata.

6. Generating garment descriptions.

7. Creating visual embeddings.

8. Packaging all outputs into a reusable template.

9. Storing templates permanently.

10. Exposing APIs for future workflows.



---



# 2. Final MVP Pipeline



Upload Images



↓



Image Validation



↓



Background Removal



↓



Mask Generation



↓



Metadata Extraction



↓



Description Generation



↓



Embedding Generation



↓



Template Packaging



↓



Storage



↓



Database Registration



---



# 3. Recommended Tech Stack



## Backend



Framework:

FastAPI



Reasons:



* High performance

* Async support

* Easy Swagger documentation

* Python ecosystem compatibility



---



## AI Models



### Validation



Model:

Florence-2 Base



Responsibilities:



* Check garment presence

* Detect multiple garments

* Detect invalid images



---



### Background Removal



Library:

rembg



Responsibilities:



* Remove background

* Generate transparent PNG



---



### Metadata Extraction



Model:

Florence-2 Base



Responsibilities:



* Garment type

* Sleeve type

* Collar type

* Gender

* Fit



---



### Description Generation



Model:

Reuse Florence-2 Base



Responsibilities:



* Produce human-readable garment summary



---



### Embeddings



Model:

OpenCLIP



Responsibilities:



* Generate similarity vectors



---



## Database



PostgreSQL



Stores:



* template metadata

* processing status

* storage paths



---



## Object Storage



MinIO



Stores:



* original images

* masks

* previews

* embeddings



---



# 4. Project Folder Structure



backend/



app/



api/



services/



models/



repositories/



workers/



storage/



schemas/



utils/



ai/



validation/



background/



metadata/



embedding/



description/



db/



tests/



---



# 5. Database Design



Table: templates



Fields:



id



template_code



name



status



preview_path



mask_path



metadata_json



description



embedding_path



created_at



updated_at



created_by



review_required



confidence_score



---



Table: template_images



Fields:



id



template_id



image_type



storage_path



created_at



---



Supported image types:



front



back



side



original



---



# 6. API Design



## Create Template



POST



/templates



Request:



multipart/form-data



Fields:



name



front_image



back_image (optional)



side_image (optional)



Response:



{

"job_id": "JOB_001",

"status": "PROCESSING"

}



---



## Get Template



GET



/templates/{template_id}



Returns:



Complete template package.



---



## List Templates



GET



/templates



Supports:



pagination



filtering



sorting



---



## Delete Template



DELETE



/templates/{template_id}



---



## Retry Failed Template



POST



/templates/{template_id}/retry



---



# 7. Processing Service Architecture



TemplateService



Responsibilities:



* Create template record

* Start processing pipeline

* Update status



Statuses:



PENDING



PROCESSING



COMPLETED



FAILED



REVIEW_REQUIRED



---



# 8. Validation Module



File:



validation_service.py



Checks:



1. File exists

2. Valid extension

3. Image readable

4. Minimum resolution

5. Garment present

6. Single garment only

7. Blur detection



Output:



{

"valid": true,

"confidence": 0.92,

"reason": null

}



Rejected images:



* corrupted

* blurry

* empty

* multiple garments



---



# 9. Background Removal Module



File:



background_service.py



Input:



front image



Process:



rembg.remove()



Outputs:



transparent PNG



preview PNG



mask PNG



Stored:



templates/TMP001/



preview.png



mask.png



transparent.png



---



# 10. Metadata Extraction Module



File:



metadata_service.py



Input:



clean garment image



Prompt:



Analyze garment image.



Return JSON only.



Extract:



garment_type



sleeve_type



collar_type



fit



gender



pocket_count



buttons



Output:



{

"garment_type": "shirt",

"sleeve_type": "full",

"collar_type": "mandarin",

"fit": "slim",

"gender": "male"

}



---



# 11. Description Service



File:



description_service.py



Input:



clean image



Output:



Natural language summary.



Example:



Men's slim-fit full-sleeve shirt with mandarin collar.



---



# 12. Embedding Service



File:



embedding_service.py



Input:



preview image



Model:



OpenCLIP



Output:



512-dimensional vector



Stored:



embedding.npy



Future Uses:



* similarity search

* recommendations

* duplicate detection



---



# 13. Template Packaging



Generated package:



templates/



TMP_0001/



preview.png



mask.png



transparent.png



metadata.json



description.txt



embedding.npy



original/



front.jpg



back.jpg



side.jpg



---



# 14. Processing Flow



Step 1



Receive upload request.



Step 2



Create DB record.



Status:



PENDING



Step 3



Store original images.



Step 4



Start processing.



Status:



PROCESSING



Step 5



Validate images.



Step 6



Remove background.



Step 7



Generate mask.



Step 8



Extract metadata.



Step 9



Generate description.



Step 10



Generate embedding.



Step 11



Package outputs.



Step 12



Store files.



Step 13



Update database.



Status:



COMPLETED



---



# 15. Error Handling



Every stage must be isolated.



Example:



try:



extract_metadata()



except:



mark status FAILED



store error message



Possible failures:



* invalid image

* model timeout

* file corruption

* storage failure



---



# 16. Logging



Log every processing stage.



Example:



Template Created



Validation Started



Validation Completed



Background Removal Completed



Metadata Extraction Completed



Embedding Generated



Template Completed



Use structured JSON logs.



---



# 17. Human Review Workflow



If confidence score < 0.75



Set:



status = REVIEW_REQUIRED



Admin can edit:



* garment type

* collar

* sleeves

* fit



After approval:



status = COMPLETED



---



# 18. Testing Plan



Unit Tests:



* image validation

* background removal

* metadata extraction

* embeddings



Integration Tests:



* complete template creation



Manual Tests:



* shirts

* kurtis

* sarees

* dresses

* jackets



---



# 19. Future Upgrade Path



Replace:



rembg → SAM2



Florence-2 → Qwen2.5-VL



OpenCLIP → FashionCLIP



No API changes required.



Only internal model services change.



---



# 20. Development Milestones



Phase 1



Project setup



FastAPI



PostgreSQL



MinIO



Swagger



---



Phase 2



Image upload APIs



Storage integration



---



Phase 3



Validation service



---



Phase 4



Background removal service



---



Phase 5



Metadata extraction service



---



Phase 6



Description generation service



---



Phase 7



Embedding generation service



---



Phase 8



Template packaging



---



Phase 9



Admin testing UI



---



Phase 10



Optimization and production deployment



---



Estimated MVP Duration



Single developer:



2–3 weeks



Small team:



1–2 weeks