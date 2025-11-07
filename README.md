# aws-project
<img width="502" height="171" alt="image" src="https://github.com/user-attachments/assets/bb3b982d-f55a-4ed8-9aa1-e2af6e43fa00" />

1.	Project Title

FileFinder:
A Serverless File Management System Using AWS Services

3.	Problem Identification
In many organizations and educational institutions, storing, searching, and managing digital files securely is a challenge. Traditional file servers or local storage systems require continuous maintenance, scaling effort, and cost. There is also a need for an efficient and accessible platform that allows users to:
•	Upload files easily.
•	Search stored files quickly using metadata or file name.
•	Delete unwanted files securely when no longer needed.
The problem therefore lies in building a cost-efficient, scalable, and serverless file management system that simplifies operations and provides real-time access to files from anywhere.

5.	Identify and Describe the Suitable AWS Services
a)	Amazon S3 (Simple Storage Service)
•	Durable, highly-available object storage for files/objects (any file type). S3 stores objects in buckets with strong durability guarantees and provides multiple ways to upload and retrieve objects.
•	Supports features like versioning, server-side encryption, pre-signed URLs, lifecycle rules, and event notifications (S3 → Lambda, S3 → EventBridge).
•	Primary file store: All user-uploaded files (student records, PDFs, text, CSVs) are stored in a dedicated bucket (filefinder-s3-bucket). This separates raw file storage from search indexes—S3 holds the authoritative copy, which is cheap and reliable.
•	Presigned URL uploads: The upload flow uses a Lambda that generates a presigned PUT URL. The frontend requests a presigned URL and then PUTs the file directly to S3. Benefits:
•	Offloads heavy file transfer from your serverless compute (no Lambda payloads for file bytes).
•	Keeps credentials safe — the browser never needs AWS keys.
•	Fine-grained control — presigned URLs can be short-lived (e.g., 60–300s).
•	Event-driven indexing: S3 ObjectiveCreated notifications trigger the indexer Lambda (S3 → Lambda). When a file is uploaded, the indexer reads the object, extracts text, chunks it, and writes metadata into DynamoDB. This decouples upload from indexing and provides near-real-time indexing.
•	Cost & scaling: S3’s low storage cost and pay-for-what-you-use model let you store dozens to millions of files cheaply during development and demo (fits AWS free tier constraints for small projects).
•	Security & compliance features used: Block public access (bucket-level), server-side encryption (SSE-S3 or SSE-KMS), and bucket policies limiting access only to necessary roles. These protect student records and ensure privacy for demo data.
•	Operational convenience: S3 integrates with CloudWatch (access logs) and lifecycle policies (auto-expire demo uploads) to keep costs and clutter low during
a class project.
Supporting Screenshots:
<img width="769" height="398" alt="image" src="https://github.com/user-attachments/assets/b2a89ced-71a3-4454-aed2-190606aff58e" />

b)	AWS Lambda
•	Serverless compute: run your code in response to events without provisioning servers. Billing is per-invocation and execution time.
•	Integrates tightly with many AWS event sources (S3, API Gateway, DynamoDB Streams, EventBridge) and can be written in multiple languages (Python, Node.js, etc.).
•	Three core Lambdas implemented:
a)	presign_upload — generates presigned PUT URLs for clients to upload directly to S3.
b)  indexer — S3-triggered function that reads uploaded files, extracts text (for txt first; extensible to PDF/docx), splits into chunks and tokens, and writes chunk records to DynamoDB.
c)	search — HTTP API–triggered function (via API Gateway) that receives a user query, computes simple token matching / filters, and returns matches with presigned GET links.
•	Event-driven architecture: Lambda lets us implement the pipeline with minimal operational overhead: S3 events → indexer, API calls → search Lambda. No servers to maintain.
•	Cost-effectiveness for student/demo scale: Free-tier generous; per-invocation billing means short demo runs are nearly free.
•	Security boundary & least-privilege: Each Lambda uses an execution role that only grants the permissions it needs: read S3 / write DynamoDB (indexer), generate presigned urls (presign lambda), dynamodb read (search). This reduces blast radius.
•	Scalability & concurrency: Lambda scales automatically for multiple concurrent uploads and searches; for a classroom demo (tens of files, a few users) default limits are sufficient.
•	Observability & debugging: CloudWatch logs from each Lambda give immediate feedback during development (indexing errors, parsing exceptions). This made debugging the file parsing and tokenization iterative and fast.

Supporting Screenshots:

<img width="959" height="340" alt="image" src="https://github.com/user-attachments/assets/948ac0e3-a48d-4ef4-abac-e2a6f6b89b3c" />
<img width="780" height="412" alt="image" src="https://github.com/user-attachments/assets/13e855b1-a831-4e9e-8031-d53abca57a83" />
<img width="929" height="399" alt="image" src="https://github.com/user-attachments/assets/0fae8388-a3eb-4f32-bbe9-dbc70f7758a5" />
<img width="870" height="522" alt="image" src="https://github.com/user-attachments/assets/52af669e-2f54-499f-9716-d56e268523cf" />

<img width="815" height="551" alt="image" src="https://github.com/user-attachments/assets/b1ded9bc-b298-456f-8d4d-b8c6354e94aa" />

c) Amazon DynamoDB
•	Fully managed, serverless NoSQL key-value and document database. Low-latency single-digit millisecond reads and writes, scalable throughput, on-demand capacity mode available.
•	Flexible items (JSON-like attributes), secondary indexes, and conditional writes.
•	Two table patterns used (or recommended):
•	FileMetadata / FileFinderRecords — store filename, S3 key, uploader info, and minimal metadata.
•	FileChunks (optional/advanced) — store chunked text segments with ChunkId, FileId, ChunkOrder, Text, and token frequencies (for more accurate search).
•	Fast query for search: DynamoDB is used as the search store. For initial simple implementation we store full file text in a metadata item and scan it during searches (sufficient for ≤100 files). For scale, we used a chunked model and inverted-index-like entries to avoid full scans.
•	Atomic writes & consistency: When indexer writes file chunks and metadata, it can use conditional writes to avoid double-indexing if re-run; DynamoDB provides predictable, safe operations.
•	Low operational overhead: No server management, backups, or patching — ideal for a student project with minimal ops knowledge.
•	Cost-control & sizing: On-demand capacity lets us avoid capacity planning during demos. For scaling up, a design with token → chunk pointers reduce read costs (instead of scanning all items).
•	How it helped the project specifically:
•	Storing parsed text makes query responses quick.
•	You can attach additional searchable keys later (uploader, tags, createdAt) without changing schema.
•	Easy integration with Lambda via boto3 (Table.put_item, scan, query) — simple CRUD.

Supporting Screenshots:

<img width="940" height="273" alt="image" src="https://github.com/user-attachments/assets/0498e461-b3bd-49d4-bd17-27030df5af8a" />

d) Amazon API Gateway (HTTP API)
•	Fully-managed service to create, secure, and operate APIs that act as “front doors” for applications. HTTP API is a lightweight, low-cost option for connecting HTTP endpoints to Lambda, services, and HTTP backends.
•	Handles routing, CORS, authorization (Cognito / IAM), throttling, and stage deployments.
•	Exposes REST endpoints for the frontend:
•	POST /upload → returns presigned URL (or accepts form-data if you choose to proxy uploads),
•	GET /search → invokes search Lambda,
•	DELETE /delete → invokes delete Lambda.
•	CORS management: API Gateway handles preflight OPTIONS so the browser-based frontend can call the API safely.
•	Security integration: You can add Cognito authorizers or API keys later; for demo we allowed open access but limited actions by role in production.
•	Mapping & proxy mode: Using Lambda proxy integration preserves the full event object (query params, headers), making it simple to parse ?student= or ?filename= parameters in the Lambdas.
•	Operational visibility & throttling: API Gateway provides request metrics and can protect your backend from bursts (useful if many students test concurrently).
•	Cost & simplicity: HTTP APIs are cheaper than REST APIs for simple routes; ideal for a student deployment.

Supporting Screenshots:


<img width="940" height="213" alt="image" src="https://github.com/user-attachments/assets/deb1f56e-a3ca-4c4f-b816-ff7a5f40adda" />

e) AWS Identity and Access Management (IAM)
•	IAM secures AWS resources by creating users, groups, roles, and policies that define who can do what to which resources.
•	Supports fine-grained, least-privilege access control and temporary credentials via role.
•	Lambda execution roles: Each Lambda has an IAM role scoped to the minimum actions necessary (e.g., indexer needs s3:GetObject and dynamodb:PutItem; presign_upload needs s3:PutObject and s3:GetObject for signing; search needs dynamodb:Scan or Query).
•	S3 → Lambda permission: We added a resource-based policy on Lambda (via aws lambda add-permission) so S3 can invoke the indexer.
•	CLI / local dev user: The IAM user you configured (aws-cli-user) has programmatic credentials used to run aws commands locally. For a classroom, we used an IAM user with broader permissions during setup and recommend restricting to least privilege afterwards.
•	Security best practice enforcement: Using IAM you can demonstrate least-privilege principles — useful for a report or lab write-up.

Supporting Screenshots:

<img width="833" height="583" alt="image" src="https://github.com/user-attachments/assets/083d6715-79ff-421d-9162-66878d0b00a6" />

<img width="946" height="222" alt="image" src="https://github.com/user-attachments/assets/8fa0b1ce-9fd0-4459-a396-6c24a74b020d" />

<img width="760" height="396" alt="image" src="https://github.com/user-attachments/assets/79213ff0-f18c-460d-a165-d7e7019c81c9" />

<img width="819" height="443" alt="image" src="https://github.com/user-attachments/assets/dc7809f9-0e0b-464c-b9ca-529f8d74fe57" />

f) Amazon CloudWatch
•	Monitoring and observability service: collects logs, metrics, traces and provides dashboards, alarms, and log insights.
•	CloudWatch Logs stores Lambda log output by default; CloudWatch Metrics shows invocation counts, duration, errors, etc.
•	Lambda debugging: CloudWatch Logs is primary place to view print/exception traces for indexer, presign, and search Lambdas — crucial when a Lambda fails to read S3, parse, or write to DynamoDB.
•	Operational monitoring: Metrics alert thresholds can be set (e.g., Lambda error rate > X), useful for detecting issues during a demo.
•	Cost & visibility: CloudWatch provides usage metrics (invocations, duration) so you can show professors how serverless costs scale.
•	Quick forensic: When a file wasn’t appearing in DynamoDB we used CloudWatch logs to find AccessDenied and ResourceNotFound exceptions and adjust IAM policies.


Supporting Screenshots:

<img width="997" height="319" alt="image" src="https://github.com/user-attachments/assets/6eb0e83d-f839-4696-8e4e-c1a1fddee976" />

4.	Workflow Diagram with Explanation
Diagram:

<img width="1120" height="570" alt="image" src="https://github.com/user-attachments/assets/821e797b-e4e1-4bcf-8f3b-d528449cd8de" />

Explanation:
The workflow diagram illustrates the seamless integration between different AWS services that collectively power the FileFinder application. It outlines how user interactions trigger various backend operations and how data flows between components to ensure a smooth, secure, and efficient experience.
1.	User Interaction (Frontend)
The process begins when a user interacts with the web-based frontend hosted locally. The user can upload, search, or delete files. Each action generates an HTTPS request that is sent to a corresponding API endpoint managed by Amazon API Gateway.
2.	Amazon API Gateway
The API Gateway acts as the single entry point for all client requests. It securely receives the requests from the frontend and routes them to the appropriate AWS Lambda function—uploadLambda, searchLambda, or deleteLambda. It ensures request validation, authorization, and proper routing without exposing the backend architecture directly.
3.	AWS Lambda Functions
o	Upload Function: When a file is uploaded, the Lambda function generates a pre-signed S3 URL, allowing the user to securely upload the file to Amazon S3 without exposing credentials. It also updates the DynamoDB table with the file’s metadata.
o	Search Function: This function queries the DynamoDB table based on search parameters (like student name or file name) and retrieves the relevant file details or content.
o	Delete Function: Upon request, this function removes both the file from S3 and its metadata record from DynamoDB, ensuring data consistency.
4.	Amazon S3 (Simple Storage Service)
Amazon S3 acts as the main storage repository for all uploaded files. It provides scalable, durable, and secure object storage. Each file uploaded through the pre-signed URL is automatically stored and can be retrieved or deleted based on user actions.
5.	Amazon DynamoDB
DynamoDB is used to maintain a structured record of all uploaded files. Each record includes essential metadata such as file name, file type, and associated student identifier. This enables fast search and retrieval operations.
6.	Execution Flow Summary
o	Upload Workflow: User → API Gateway → Lambda (Upload) → S3 + DynamoDB
o	Search Workflow: User → API Gateway → Lambda (Search) → DynamoDB → Response to User
o	Delete Workflow: User → API Gateway → Lambda (Delete) → S3 + DynamoDB
7.	Benefits of the Architecture
This serverless architecture ensures scalability, cost-efficiency, and security. AWS Lambda eliminates the need for manual server management, while S3 and DynamoDB provide robust storage and querying capabilities. The system can easily handle multiple concurrent users and file operations without performance degradation.


5.	Application Development
The application is developed as a fully serverless web-based system with three key functionalities: upload, search, and delete.
1.	Backend Development:
o	Three Lambda functions were created for upload, search, and delete operations.
o	The upload function generates a pre signed S3 URL to allow direct file uploads.
o	The search function retrieves file information from DynamoDB.
o	The delete function removes the selected file from both S3 and DynamoDB.
o	API Gateway endpoints were configured to expose these Lambda functions as HTTP APIs.
2.	Database and Storage Configuration:
o	An S3 bucket (filefinder-s3-bucket) was created for storing user files.
o	A DynamoDB table (FileFinder Records) was created with filename as the primary key.
3.	Frontend Development:
o	A minimal and elegant web interface was built using HTML, CSS, and JavaScript.
o	Users can upload files, search by name, and delete files directly through the interface.
o	The frontend interacts with the backend via API Gateway endpoints.
4.	Testing and Deployment:
o	Lambda functions were tested individually using AWS Console test events.
o	API endpoints were validated using PowerShell Invoke-Web Request and curl commands.
o	After successful testing, the frontend was connected to the backend for end-to-end functionality.


6.	Sample Screenshots
Method 1: Via CLI
a)	Downloading CLI

<img width="1085" height="176" alt="image" src="https://github.com/user-attachments/assets/699389a3-4a3a-48d7-b38c-9c8e7aee26d9" />
b) Configuring

<img width="1187" height="275" alt="image" src="https://github.com/user-attachments/assets/c64f9d6f-b3c9-4d6b-89a4-3644d44468d5" />

c) Creating and Listing Buckets 

<img width="941" height="130" alt="image" src="https://github.com/user-attachments/assets/20936ece-b6a3-4085-8460-0b79ad71ddc9" />

<img width="1362" height="79" alt="image" src="https://github.com/user-attachments/assets/97c21e81-6b13-49d2-8b0a-90075351d5b5" />


d) Adding permissions and files 

<img width="1362" height="454" alt="image" src="https://github.com/user-attachments/assets/f42c8389-bf1e-41fd-8829-7419d98083d1" />

e) Uploading

<img width="908" height="456" alt="image" src="https://github.com/user-attachments/assets/f2af10bc-a874-49d1-87d6-1fb42edaadab" />


f) Searching 

<img width="940" height="75" alt="image" src="https://github.com/user-attachments/assets/87fb2d2f-0d1a-4ac3-9d53-8cd52cfecc94" />

 g) Deleting 


<img width="737" height="351" alt="image" src="https://github.com/user-attachments/assets/2251d6da-807e-47bc-9c55-3c9ae9fbbf98" />

Method 2: Via Frontend Section (UI/UX)
1.)	Showing all the implemented features 

<img width="940" height="510" alt="image" src="https://github.com/user-attachments/assets/7d98f77b-a505-416d-9b88-371ca8103ecf" />

2.) Upload Feature 

<img width="932" height="532" alt="image" src="https://github.com/user-attachments/assets/4eb4096d-facb-4931-81c7-06fe9cb22b7b" />

3.) Search Feature


<img width="932" height="1226" alt="image" src="https://github.com/user-attachments/assets/e4e8cb4c-0bae-4708-81f6-ddc54d0bb6ad" />

4.) Delete Feature 


<img width="932" height="1226" alt="image" src="https://github.com/user-attachments/assets/8ae747dc-3ec9-41fe-a805-fc5a9a5429e2" />










