# Candidate static-validation evidence

These are trusted scanner observations against AI-authored, unapproved labels. They are not a quality benchmark, human approval, or runtime test.

Recorded cases: **204/204**. Model calls: **0**. Human approvals created: **0**.

## Frozen environment

```json
{
  "profile": "security-v2",
  "profile_digests": {
    "source": "221377c54607dc61fe0f2097c0a4f8f87557847ed2ee877cd743a889a9c82d21",
    "dependency": "825b4d8e4f90e37819584a9154b18670e4dfe7eb6982164e688fad910cc20d36"
  },
  "tools": [
    {
      "id": "bandit",
      "version": "bandit 1.9.4",
      "expected_version": "1.9.4",
      "available": true
    },
    {
      "id": "depcheck",
      "version": "Version: 0.74.0",
      "expected_version": "0.74.0",
      "available": true
    },
    {
      "id": "dotnet",
      "version": "codeagent-dotnet 1.1.0",
      "expected_version": "codeagent-dotnet 1.1.0",
      "available": true
    },
    {
      "id": "semgrep",
      "version": "1.178.0",
      "expected_version": "1.178.0",
      "available": true
    }
  ]
}
```

## Case observations

| Case | Execution | Parser/check coverage | Proposed-label agreement | Evidence |
| --- | --- | --- | --- | --- |
| v2-bash-safe-01 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-bash-safe-01-d4040ac4-f1f2-46b3-8b53-fb55edd23118.json) |
| v2-bash-safe-02 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-bash-safe-02-5cf2ba16-71e0-4121-b8b5-8d13e6f66918.json) |
| v2-bash-safe-03 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-bash-safe-03-3d31087b-5806-4840-b109-3d9100934753.json) |
| v2-bash-safe-04 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-bash-safe-04-34f80be3-1a8f-412d-94c3-2f77a9af8903.json) |
| v2-bash-safe-05 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-bash-safe-05-4981ce46-fa88-47fd-b539-9981bc994d50.json) |
| v2-bash-safe-06 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-bash-safe-06-9611b9c4-4419-42ad-8661-d64c389caa34.json) |
| v2-bash-vulnerable-01 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-bash-vulnerable-01-5a8c5f12-5335-42a4-90e8-37c82026fafe.json) |
| v2-bash-vulnerable-02 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-bash-vulnerable-02-21b7c282-12ef-4073-8472-e94016e34c10.json) |
| v2-bash-vulnerable-03 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-bash-vulnerable-03-92ab1cfa-72de-4ff2-97b0-c1b5886f954f.json) |
| v2-bash-vulnerable-04 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-bash-vulnerable-04-97302649-7b41-4d72-9b67-368c60cd2351.json) |
| v2-bash-vulnerable-05 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-bash-vulnerable-05-75acad8e-381e-4db9-8799-fa5f56255a59.json) |
| v2-bash-vulnerable-06 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-bash-vulnerable-06-0fc12e4c-7035-456f-b396-71bec6f5b058.json) |
| v2-c-safe-01 | completed | completed | matches_proposed_labels | [Report](reports/v2-c-safe-01-577bdfa2-3c7f-48fb-9de8-2eafa3d3d727.json) |
| v2-c-safe-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-c-safe-02-48f772ae-14ed-4881-bee7-c58957dbc1b7.json) |
| v2-c-safe-03 | completed | completed | matches_proposed_labels | [Report](reports/v2-c-safe-03-399f4729-c097-4eff-9cf1-e5604a9ac394.json) |
| v2-c-safe-04 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-c-safe-04-21a4c453-f2a4-4834-84f5-eeea285b4a2a.json) |
| v2-c-safe-05 | completed | completed | matches_proposed_labels | [Report](reports/v2-c-safe-05-aad25efd-f946-4b7d-88fb-a2b31d12579f.json) |
| v2-c-safe-06 | completed | completed | matches_proposed_labels | [Report](reports/v2-c-safe-06-2c383cfb-5cd5-4baf-8235-9971050ce839.json) |
| v2-c-vulnerable-01 | completed | completed | expected_not_observed | [Report](reports/v2-c-vulnerable-01-96759ad4-0e5d-4c6d-8fcf-4b752e1be9fb.json) |
| v2-c-vulnerable-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-c-vulnerable-02-abf2c41c-5ba4-447f-a2a7-624f44aebb54.json) |
| v2-c-vulnerable-03 | completed | completed | matches_proposed_labels | [Report](reports/v2-c-vulnerable-03-26af4a49-6756-414d-ac8f-cf11b640afb1.json) |
| v2-c-vulnerable-04 | completed | completed | expected_not_observed | [Report](reports/v2-c-vulnerable-04-9570f7d7-3029-46fb-98e3-5e654da8d7ad.json) |
| v2-c-vulnerable-05 | completed | completed | matches_proposed_labels | [Report](reports/v2-c-vulnerable-05-eb6e3d0f-43e9-4bf4-b08c-3e9c636593c8.json) |
| v2-c-vulnerable-06 | completed | completed | expected_not_observed | [Report](reports/v2-c-vulnerable-06-75907617-d91e-4ae5-a970-6fb324a2bcd4.json) |
| v2-cpp-safe-01 | completed | completed | matches_proposed_labels | [Report](reports/v2-cpp-safe-01-16f2ecd8-2aff-4cad-b9f2-4497ce6dec08.json) |
| v2-cpp-safe-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-cpp-safe-02-5e3e3e07-ffa4-40a1-9f54-a56fbc424330.json) |
| v2-cpp-safe-03 | completed | completed | matches_proposed_labels | [Report](reports/v2-cpp-safe-03-dbafb182-dcdd-46d8-b074-a6c5909280ae.json) |
| v2-cpp-safe-04 | completed | completed | matches_proposed_labels | [Report](reports/v2-cpp-safe-04-05508554-6220-4e38-80d1-e6fc579ae865.json) |
| v2-cpp-safe-05 | completed | completed | matches_proposed_labels | [Report](reports/v2-cpp-safe-05-aaf1bf53-c76a-42ee-a5ba-446b63204130.json) |
| v2-cpp-safe-06 | completed | completed | matches_proposed_labels | [Report](reports/v2-cpp-safe-06-3f7a03b8-80bf-4b92-9dae-0b35d218bd12.json) |
| v2-cpp-vulnerable-01 | completed | completed | expected_not_observed | [Report](reports/v2-cpp-vulnerable-01-cb013dd2-0b19-437b-a46f-7234d1b7a10e.json) |
| v2-cpp-vulnerable-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-cpp-vulnerable-02-3106dbb7-c4d1-4896-a8bd-9bb8b3e8b681.json) |
| v2-cpp-vulnerable-03 | completed | completed | expected_not_observed | [Report](reports/v2-cpp-vulnerable-03-2b6e0ecb-8bcf-420a-9f58-d23d11fb29ac.json) |
| v2-cpp-vulnerable-04 | completed | completed | expected_not_observed | [Report](reports/v2-cpp-vulnerable-04-8aba0a9b-1ac8-486b-b4af-8650c8df19c7.json) |
| v2-cpp-vulnerable-05 | completed | completed | expected_not_observed | [Report](reports/v2-cpp-vulnerable-05-76910925-682b-4e07-8888-0150db148cd1.json) |
| v2-cpp-vulnerable-06 | completed | completed | expected_not_observed | [Report](reports/v2-cpp-vulnerable-06-469e5696-24e9-430c-a93f-f7e5038fbda2.json) |
| v2-csharp-safe-01 | completed | completed | matches_proposed_labels | [Report](reports/v2-csharp-safe-01-e49cd57d-8894-4ac4-bdca-921b5f4e3362.json) |
| v2-csharp-safe-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-csharp-safe-02-6e34262e-2876-4cff-81b1-713aebda0a34.json) |
| v2-csharp-safe-03 | completed | completed | matches_proposed_labels | [Report](reports/v2-csharp-safe-03-59336818-b909-4138-a674-48f1b74e64b0.json) |
| v2-csharp-safe-04 | completed | completed | matches_proposed_labels | [Report](reports/v2-csharp-safe-04-5c93b5ad-0e0e-47e5-a973-26d045ba998d.json) |
| v2-csharp-safe-05 | completed | completed | matches_proposed_labels | [Report](reports/v2-csharp-safe-05-a84e5e68-e1ee-469e-92e2-957e27c8d804.json) |
| v2-csharp-safe-06 | completed | completed | matches_proposed_labels | [Report](reports/v2-csharp-safe-06-690d243d-9470-44d3-8445-60375b872cbd.json) |
| v2-csharp-vulnerable-01 | completed | completed | expected_not_observed | [Report](reports/v2-csharp-vulnerable-01-a6149e81-0593-48b7-9cc8-04ff9debe6e9.json) |
| v2-csharp-vulnerable-02 | completed | completed | expected_not_observed | [Report](reports/v2-csharp-vulnerable-02-0d79aeb3-6518-47c2-aad8-cbef4f36c818.json) |
| v2-csharp-vulnerable-03 | completed | completed | expected_not_observed | [Report](reports/v2-csharp-vulnerable-03-b0d3b9f5-b1ce-4eb9-a292-1c8b6f92ef4b.json) |
| v2-csharp-vulnerable-04 | completed | completed | matches_proposed_labels | [Report](reports/v2-csharp-vulnerable-04-3f97e9db-e38f-49a7-818f-ef19a7bca1a7.json) |
| v2-csharp-vulnerable-05 | completed | completed | matches_proposed_labels | [Report](reports/v2-csharp-vulnerable-05-380acf71-df97-4bb6-9c7e-5e9ff018bb43.json) |
| v2-csharp-vulnerable-06 | completed | completed | matches_proposed_labels | [Report](reports/v2-csharp-vulnerable-06-a19ad035-0e65-4ee4-bf5f-b25e74fea82e.json) |
| v2-fsharp-safe-01 | completed | completed | matches_proposed_labels | [Report](reports/v2-fsharp-safe-01-9df9120e-fcfb-4d03-b2e4-df420da77d5f.json) |
| v2-fsharp-safe-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-fsharp-safe-02-d661d326-b100-4288-be0f-9a76202cac2f.json) |
| v2-fsharp-safe-03 | completed | completed | matches_proposed_labels | [Report](reports/v2-fsharp-safe-03-ae24b1c0-3440-4a8f-9bbe-5ff13e82d8ad.json) |
| v2-fsharp-safe-04 | completed | completed | matches_proposed_labels | [Report](reports/v2-fsharp-safe-04-d573daeb-608f-4a31-b108-2a20194d22fb.json) |
| v2-fsharp-safe-05 | completed | completed | matches_proposed_labels | [Report](reports/v2-fsharp-safe-05-555357d5-d224-457d-baf3-cac31385ea21.json) |
| v2-fsharp-safe-06 | completed | completed | matches_proposed_labels | [Report](reports/v2-fsharp-safe-06-53fa9fda-d6e5-4989-bff8-f8480860d79d.json) |
| v2-fsharp-vulnerable-01 | completed | completed | expected_not_observed | [Report](reports/v2-fsharp-vulnerable-01-767eec7f-a408-41f9-a89c-192a15f00f44.json) |
| v2-fsharp-vulnerable-02 | completed | completed | expected_not_observed | [Report](reports/v2-fsharp-vulnerable-02-0a499c42-3b5c-4b32-b1c2-7b51d877c5a7.json) |
| v2-fsharp-vulnerable-03 | completed | completed | unexpected_findings | [Report](reports/v2-fsharp-vulnerable-03-8516566e-c536-42a2-8e7e-35a21bc715a9.json) |
| v2-fsharp-vulnerable-04 | completed | completed | missing_and_unexpected | [Report](reports/v2-fsharp-vulnerable-04-bc11b6dc-c07f-4205-8b8a-07401badb98b.json) |
| v2-fsharp-vulnerable-05 | completed | completed | expected_not_observed | [Report](reports/v2-fsharp-vulnerable-05-dc163321-4065-4b9b-975e-b68e8df535ce.json) |
| v2-fsharp-vulnerable-06 | completed | completed | expected_not_observed | [Report](reports/v2-fsharp-vulnerable-06-37e511d4-488d-4a5c-85e3-6306e18660a8.json) |
| v2-go-safe-01 | completed | completed | matches_proposed_labels | [Report](reports/v2-go-safe-01-a341ad6e-46d7-4997-b493-246727af7c5c.json) |
| v2-go-safe-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-go-safe-02-8936ff0d-7310-453e-8cfc-671816732a47.json) |
| v2-go-safe-03 | completed | completed | matches_proposed_labels | [Report](reports/v2-go-safe-03-f4de630a-ad94-4ac6-81e0-43cbab36cc56.json) |
| v2-go-safe-04 | completed | completed | matches_proposed_labels | [Report](reports/v2-go-safe-04-e2e212ed-5c88-457c-a98e-792d4a819373.json) |
| v2-go-safe-05 | completed | completed | matches_proposed_labels | [Report](reports/v2-go-safe-05-1f791572-372d-4076-8d81-53d4f317e743.json) |
| v2-go-safe-06 | completed | completed | matches_proposed_labels | [Report](reports/v2-go-safe-06-2ee9c96d-7c0f-4cb9-9880-2785abc9d0a1.json) |
| v2-go-vulnerable-01 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-go-vulnerable-01-a2130522-6302-4c29-b637-7d1dc1863fa3.json) |
| v2-go-vulnerable-02 | completed | completed | expected_not_observed | [Report](reports/v2-go-vulnerable-02-049c1e0e-dfb4-4b8c-94fc-a1d9aa1167a5.json) |
| v2-go-vulnerable-03 | completed | completed | expected_not_observed | [Report](reports/v2-go-vulnerable-03-834100dd-4ed5-40bd-afb8-8db0523c81de.json) |
| v2-go-vulnerable-04 | completed | completed | expected_not_observed | [Report](reports/v2-go-vulnerable-04-fc5976c5-5cfa-402c-a054-4552ca76847f.json) |
| v2-go-vulnerable-05 | completed | completed | expected_not_observed | [Report](reports/v2-go-vulnerable-05-38c0d03a-0b48-49e7-8471-d03ca6093419.json) |
| v2-go-vulnerable-06 | completed | completed | expected_not_observed | [Report](reports/v2-go-vulnerable-06-9d392817-d32c-43ba-9eef-8b181b0eb5cc.json) |
| v2-java-safe-01 | completed | completed | matches_proposed_labels | [Report](reports/v2-java-safe-01-d1f47e91-6c4d-4114-9cad-124624378eed.json) |
| v2-java-safe-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-java-safe-02-63d9ebf1-25c9-4389-91e7-2f20a014365d.json) |
| v2-java-safe-03 | completed | completed | matches_proposed_labels | [Report](reports/v2-java-safe-03-d92bc468-6a8f-4c72-8e2a-810931062db5.json) |
| v2-java-safe-04 | completed | completed | matches_proposed_labels | [Report](reports/v2-java-safe-04-6cbabfb6-a0a1-4016-a147-15f71a17823e.json) |
| v2-java-safe-05 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-java-safe-05-bce0046b-6524-4668-bfac-2b8722aca14a.json) |
| v2-java-safe-06 | completed | completed | matches_proposed_labels | [Report](reports/v2-java-safe-06-1c4cc416-f041-4ea8-818a-c71e47b0cb2d.json) |
| v2-java-vulnerable-01 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-java-vulnerable-01-31c136b8-4553-4e38-b515-fa920d9f3f92.json) |
| v2-java-vulnerable-02 | completed | completed | expected_not_observed | [Report](reports/v2-java-vulnerable-02-ee5d792d-c671-4074-a2c6-f8789e1e0a7c.json) |
| v2-java-vulnerable-03 | completed | completed | expected_not_observed | [Report](reports/v2-java-vulnerable-03-6489e408-5c9a-4f78-854c-3e43a06d5daa.json) |
| v2-java-vulnerable-04 | completed | completed | expected_not_observed | [Report](reports/v2-java-vulnerable-04-7b5a605c-48bd-4448-afb4-f8838706eed8.json) |
| v2-java-vulnerable-05 | completed | completed | matches_proposed_labels | [Report](reports/v2-java-vulnerable-05-24ef3ce5-8466-423e-8fba-cd64f8fbc33c.json) |
| v2-java-vulnerable-06 | completed | completed | expected_not_observed | [Report](reports/v2-java-vulnerable-06-d415e2c7-8c39-41f7-805e-be63f0851664.json) |
| v2-javascript-safe-01 | completed | completed | matches_proposed_labels | [Report](reports/v2-javascript-safe-01-f17a3578-07ab-4a01-89db-85e65cae5f18.json) |
| v2-javascript-safe-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-javascript-safe-02-f094b06b-5822-4d50-be3a-1561d11d175c.json) |
| v2-javascript-safe-03 | completed | completed | matches_proposed_labels | [Report](reports/v2-javascript-safe-03-3e6904f1-ec15-42d0-b3f4-f1a0727ba32e.json) |
| v2-javascript-safe-04 | completed | completed | matches_proposed_labels | [Report](reports/v2-javascript-safe-04-95ca76a8-82f9-421b-824e-554978db4edd.json) |
| v2-javascript-safe-05 | completed | completed | matches_proposed_labels | [Report](reports/v2-javascript-safe-05-cb827e1f-0ad1-4adf-9ff7-993cd951b842.json) |
| v2-javascript-safe-06 | completed | completed | matches_proposed_labels | [Report](reports/v2-javascript-safe-06-e6948b48-ee6a-4c7e-8a78-b66b597850cf.json) |
| v2-javascript-vulnerable-01 | completed | completed | expected_not_observed | [Report](reports/v2-javascript-vulnerable-01-ae7a724e-7eea-4a7c-9da3-677fd17add57.json) |
| v2-javascript-vulnerable-02 | completed | completed | expected_not_observed | [Report](reports/v2-javascript-vulnerable-02-2f6df7c9-9eb7-47b9-8319-aa60a9f6d802.json) |
| v2-javascript-vulnerable-03 | completed | completed | expected_not_observed | [Report](reports/v2-javascript-vulnerable-03-7cc56c09-03ac-4995-b058-ceec962929cb.json) |
| v2-javascript-vulnerable-04 | completed | completed | expected_not_observed | [Report](reports/v2-javascript-vulnerable-04-2439d254-4c11-4ec3-b051-1a5e1e2fe6ba.json) |
| v2-javascript-vulnerable-05 | completed | completed | expected_not_observed | [Report](reports/v2-javascript-vulnerable-05-aa7cd379-ff90-4a5f-aa6e-b80317a8f0e8.json) |
| v2-javascript-vulnerable-06 | completed | completed | expected_not_observed | [Report](reports/v2-javascript-vulnerable-06-cfaf098f-a611-4539-a9f5-ab21724302c2.json) |
| v2-kotlin-safe-01 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-kotlin-safe-01-f4bda8d2-cee4-4117-aa1e-8db023d1f102.json) |
| v2-kotlin-safe-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-kotlin-safe-02-93aa4220-12af-4b61-8072-19df75daa1a5.json) |
| v2-kotlin-safe-03 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-kotlin-safe-03-4cd50adc-ea36-4ab0-8c8e-8541a07c9078.json) |
| v2-kotlin-safe-04 | completed | completed | unexpected_findings | [Report](reports/v2-kotlin-safe-04-93abe0b2-d46f-49f5-8861-0e27dac96ec3.json) |
| v2-kotlin-safe-05 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-kotlin-safe-05-8b1ceb11-0390-41f2-91ae-814e188a2810.json) |
| v2-kotlin-safe-06 | completed | completed | matches_proposed_labels | [Report](reports/v2-kotlin-safe-06-73c3d301-7159-4142-9a95-50afc6b13374.json) |
| v2-kotlin-vulnerable-01 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-kotlin-vulnerable-01-a76a43a4-0df0-4efc-a92f-d2f3373ca71d.json) |
| v2-kotlin-vulnerable-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-kotlin-vulnerable-02-ec6bfefa-4044-4790-91ca-29975a0c8e0c.json) |
| v2-kotlin-vulnerable-03 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-kotlin-vulnerable-03-2faf19b6-1eeb-4657-9e3f-6a0c678e1203.json) |
| v2-kotlin-vulnerable-04 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-kotlin-vulnerable-04-8f464c17-1789-4ebd-9392-a2b0e107dae6.json) |
| v2-kotlin-vulnerable-05 | completed | completed | expected_not_observed | [Report](reports/v2-kotlin-vulnerable-05-3a68b63d-b949-4c8f-8fdc-c0c763d3a7b5.json) |
| v2-kotlin-vulnerable-06 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-kotlin-vulnerable-06-4b2e49bd-8d0d-4892-8fdc-a97976cb1227.json) |
| v2-php-safe-01 | completed | completed | matches_proposed_labels | [Report](reports/v2-php-safe-01-9671b1b0-198b-4439-8ea1-adf19f280441.json) |
| v2-php-safe-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-php-safe-02-0dfd81e6-4e4b-4dbf-853e-d5bea7169b3d.json) |
| v2-php-safe-03 | completed | completed | matches_proposed_labels | [Report](reports/v2-php-safe-03-fa0bebe1-5354-4f23-b202-5b692c097049.json) |
| v2-php-safe-04 | completed | completed | matches_proposed_labels | [Report](reports/v2-php-safe-04-6fa41779-435f-4393-8a97-c383663349ea.json) |
| v2-php-safe-05 | completed | completed | matches_proposed_labels | [Report](reports/v2-php-safe-05-df58f5d2-0d56-4541-9c6d-b079bb04ef7e.json) |
| v2-php-safe-06 | completed | completed | matches_proposed_labels | [Report](reports/v2-php-safe-06-c1889039-b11f-4935-b81b-87e04da82f33.json) |
| v2-php-vulnerable-01 | completed | completed | expected_not_observed | [Report](reports/v2-php-vulnerable-01-c4302e12-24ec-485a-9270-3e57987e5fe8.json) |
| v2-php-vulnerable-02 | completed | completed | expected_not_observed | [Report](reports/v2-php-vulnerable-02-567bf7e3-1644-48b2-84b4-990c7704a11f.json) |
| v2-php-vulnerable-03 | completed | completed | expected_not_observed | [Report](reports/v2-php-vulnerable-03-4d79f033-5c49-452a-84b1-fd48cce66c3b.json) |
| v2-php-vulnerable-04 | completed | completed | expected_not_observed | [Report](reports/v2-php-vulnerable-04-fbf1b2e6-5dbf-49fd-8263-1da1ef3191b4.json) |
| v2-php-vulnerable-05 | completed | completed | matches_proposed_labels | [Report](reports/v2-php-vulnerable-05-a9a408c6-3804-4fe2-a72e-9821a86fbf93.json) |
| v2-php-vulnerable-06 | completed | completed | expected_not_observed | [Report](reports/v2-php-vulnerable-06-748f5e83-db01-4856-a4e9-078e3b656e78.json) |
| v2-python-safe-01 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-python-safe-01-9f760179-2b89-4e9a-9448-ba47de9a3b8b.json) |
| v2-python-safe-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-python-safe-02-d3541047-47e3-4db6-aecd-01ed38febe31.json) |
| v2-python-safe-03 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-python-safe-03-5e3a5815-4dfc-4584-81aa-a372109bcd49.json) |
| v2-python-safe-04 | completed | completed | unexpected_findings | [Report](reports/v2-python-safe-04-7e7c114d-5142-4150-8971-f7b98b1a329f.json) |
| v2-python-safe-05 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-python-safe-05-f08773ee-6487-469a-8e7a-3a96439b91c0.json) |
| v2-python-safe-06 | completed | completed | matches_proposed_labels | [Report](reports/v2-python-safe-06-0a8ff7c6-588e-48d3-8111-7aee36e33038.json) |
| v2-python-vulnerable-01 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-python-vulnerable-01-5f1f49c6-5854-4379-bb6f-4338a3a666be.json) |
| v2-python-vulnerable-02 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-python-vulnerable-02-b28c9ad7-7004-4404-b127-e0f94f583c3b.json) |
| v2-python-vulnerable-03 | completed | completed | expected_not_observed | [Report](reports/v2-python-vulnerable-03-ecc9b021-eeab-4903-b2ae-e9f62782ff7c.json) |
| v2-python-vulnerable-04 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-python-vulnerable-04-652ceda9-fc69-4958-86dd-71d6080e4880.json) |
| v2-python-vulnerable-05 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-python-vulnerable-05-ad90cf52-22dc-4e44-90e4-5f3f871209b1.json) |
| v2-python-vulnerable-06 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-python-vulnerable-06-a28fd1f8-6a3a-4e49-ba33-e033835e9dea.json) |
| v2-ruby-safe-01 | completed | completed | matches_proposed_labels | [Report](reports/v2-ruby-safe-01-865fb6d6-9b0c-4b66-9b26-3f3866a3626d.json) |
| v2-ruby-safe-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-ruby-safe-02-07a7b056-9cc3-4eef-947c-3d3dd3e7d5bb.json) |
| v2-ruby-safe-03 | completed | completed | matches_proposed_labels | [Report](reports/v2-ruby-safe-03-3baa7967-66b9-4912-b4bf-82ba4fc306b8.json) |
| v2-ruby-safe-04 | completed | completed | matches_proposed_labels | [Report](reports/v2-ruby-safe-04-808373c5-15db-4850-97be-c5f5a3750bc8.json) |
| v2-ruby-safe-05 | completed | completed | matches_proposed_labels | [Report](reports/v2-ruby-safe-05-3f7f2ab3-6525-4460-820f-d5ea943bb9c7.json) |
| v2-ruby-safe-06 | completed | completed | matches_proposed_labels | [Report](reports/v2-ruby-safe-06-b7587ddc-1cdf-4262-9dee-bb26e522beb3.json) |
| v2-ruby-vulnerable-01 | completed | completed | expected_not_observed | [Report](reports/v2-ruby-vulnerable-01-3c4cc011-81a0-46e1-8211-6bc3ace382f6.json) |
| v2-ruby-vulnerable-02 | completed | completed | expected_not_observed | [Report](reports/v2-ruby-vulnerable-02-f8309320-1f14-477a-8f91-0445296f4dd1.json) |
| v2-ruby-vulnerable-03 | completed | completed | expected_not_observed | [Report](reports/v2-ruby-vulnerable-03-1eed8c4d-fb60-4bf0-ba0f-6a6a96480740.json) |
| v2-ruby-vulnerable-04 | completed | completed | expected_not_observed | [Report](reports/v2-ruby-vulnerable-04-28f5a2a5-fa96-4a82-b9e1-b56e88b3d7c2.json) |
| v2-ruby-vulnerable-05 | completed | completed | expected_not_observed | [Report](reports/v2-ruby-vulnerable-05-9426c154-fa9a-4fa5-8b2c-757b6106d11c.json) |
| v2-ruby-vulnerable-06 | completed | completed | expected_not_observed | [Report](reports/v2-ruby-vulnerable-06-50c0e304-ca56-48b6-87ae-a9b779688312.json) |
| v2-rust-safe-01 | completed | completed | matches_proposed_labels | [Report](reports/v2-rust-safe-01-c7d96346-d66a-4dbe-ac8b-010e5194815b.json) |
| v2-rust-safe-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-rust-safe-02-936572f6-b4f9-4baf-979c-3ac16d5df107.json) |
| v2-rust-safe-03 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-rust-safe-03-00bc1bdb-0d37-40af-a461-df5c108df0c1.json) |
| v2-rust-safe-04 | completed | completed | matches_proposed_labels | [Report](reports/v2-rust-safe-04-5957bdd6-0529-44b3-b47c-e581cc247241.json) |
| v2-rust-safe-05 | completed | completed | matches_proposed_labels | [Report](reports/v2-rust-safe-05-efe92cf1-111d-4f6d-938b-1b4849dabaf5.json) |
| v2-rust-safe-06 | completed | completed | matches_proposed_labels | [Report](reports/v2-rust-safe-06-27e95488-ea28-4089-aa22-bcf11f9e365a.json) |
| v2-rust-vulnerable-01 | completed | completed | expected_not_observed | [Report](reports/v2-rust-vulnerable-01-34ba0669-2e0e-4fb2-8048-d1e0b8612045.json) |
| v2-rust-vulnerable-02 | completed | completed | expected_not_observed | [Report](reports/v2-rust-vulnerable-02-34fb20b4-f3d2-4721-860b-6094c1bb259d.json) |
| v2-rust-vulnerable-03 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-rust-vulnerable-03-d9291d82-59c7-4386-8321-6932611916b0.json) |
| v2-rust-vulnerable-04 | completed | completed | matches_proposed_labels | [Report](reports/v2-rust-vulnerable-04-17415a15-ba80-47aa-8955-bf4bed2175c4.json) |
| v2-rust-vulnerable-05 | completed | completed | expected_not_observed | [Report](reports/v2-rust-vulnerable-05-9898c41e-214e-40c2-8179-ef80a25d8d6e.json) |
| v2-rust-vulnerable-06 | completed | completed | expected_not_observed | [Report](reports/v2-rust-vulnerable-06-a4df3bae-6680-41e8-be09-480554526777.json) |
| v2-scala-safe-01 | completed | completed | matches_proposed_labels | [Report](reports/v2-scala-safe-01-a35c0b7e-ffda-4f7d-ad9d-8e0cc36e225b.json) |
| v2-scala-safe-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-scala-safe-02-6fcc4055-2427-49fc-91b4-d0c504035971.json) |
| v2-scala-safe-03 | completed | completed | matches_proposed_labels | [Report](reports/v2-scala-safe-03-8025e70c-34a9-46ed-bae9-c201302f70a1.json) |
| v2-scala-safe-04 | completed | completed | matches_proposed_labels | [Report](reports/v2-scala-safe-04-c5a6eb21-fa77-4573-b7f8-ccbbd8c03509.json) |
| v2-scala-safe-05 | completed | completed | matches_proposed_labels | [Report](reports/v2-scala-safe-05-fc244e12-8387-4318-b9ef-a18497d616fc.json) |
| v2-scala-safe-06 | completed | completed | matches_proposed_labels | [Report](reports/v2-scala-safe-06-b757ad4d-850e-429c-8a8d-324b05044f08.json) |
| v2-scala-vulnerable-01 | completed | completed | expected_not_observed | [Report](reports/v2-scala-vulnerable-01-df03aff4-10d1-49f1-b24f-25313a2d4a10.json) |
| v2-scala-vulnerable-02 | completed | completed | expected_not_observed | [Report](reports/v2-scala-vulnerable-02-8668679d-ab95-4e22-a40f-64e4da8b473e.json) |
| v2-scala-vulnerable-03 | completed | completed | expected_not_observed | [Report](reports/v2-scala-vulnerable-03-3cf10362-b89c-460a-ad4c-a2e1526af7f1.json) |
| v2-scala-vulnerable-04 | completed | completed | expected_not_observed | [Report](reports/v2-scala-vulnerable-04-b02660a6-0eff-4d77-af6e-395c51f9c951.json) |
| v2-scala-vulnerable-05 | completed | completed | expected_not_observed | [Report](reports/v2-scala-vulnerable-05-2dfc19fd-703e-45dc-86b2-f00a2c1d40cc.json) |
| v2-scala-vulnerable-06 | completed | completed | expected_not_observed | [Report](reports/v2-scala-vulnerable-06-f640dc04-ef39-4a55-a76a-932e3c388a8e.json) |
| v2-swift-safe-01 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-swift-safe-01-83d80825-31b6-44c4-a312-1fe58f547d43.json) |
| v2-swift-safe-02 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-swift-safe-02-ec245dd0-13b9-4c3d-bd44-4f60d0a803f0.json) |
| v2-swift-safe-03 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-swift-safe-03-65012fa4-15a7-48ce-8bb8-52985df980cf.json) |
| v2-swift-safe-04 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-swift-safe-04-98cb71ea-33b4-4d7a-8ad9-50a4442b104f.json) |
| v2-swift-safe-05 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-swift-safe-05-c2c67fe6-2e48-4aad-96fb-710c7901d229.json) |
| v2-swift-safe-06 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-swift-safe-06-b6b10fc7-691d-4bba-8ba2-37940b9ca545.json) |
| v2-swift-vulnerable-01 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-swift-vulnerable-01-52886e2c-2500-403a-bc57-67516159efcc.json) |
| v2-swift-vulnerable-02 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-swift-vulnerable-02-35ffc98a-4b81-4895-a174-97af8adafdce.json) |
| v2-swift-vulnerable-03 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-swift-vulnerable-03-26240868-25ba-4583-a4e1-bab839b8cce8.json) |
| v2-swift-vulnerable-04 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-swift-vulnerable-04-f96857c4-52de-46c6-b1c1-35284beffa6a.json) |
| v2-swift-vulnerable-05 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-swift-vulnerable-05-84fd2c49-c080-4951-af6b-c579864c8677.json) |
| v2-swift-vulnerable-06 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-swift-vulnerable-06-31d1983a-3d94-4d9a-bf48-a02a8b0f53b8.json) |
| v2-typescript-safe-01 | completed | completed | matches_proposed_labels | [Report](reports/v2-typescript-safe-01-dd74fdf9-1642-4603-9a41-3034d82f2f40.json) |
| v2-typescript-safe-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-typescript-safe-02-f95c7545-9c16-4321-addf-605a1c1fb199.json) |
| v2-typescript-safe-03 | completed | completed | matches_proposed_labels | [Report](reports/v2-typescript-safe-03-018bc6e5-f74a-4878-a852-3f7db6fcefd6.json) |
| v2-typescript-safe-04 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-typescript-safe-04-b8a404b2-effb-4a98-8d53-33fced37351d.json) |
| v2-typescript-safe-05 | completed | completed | matches_proposed_labels | [Report](reports/v2-typescript-safe-05-2beda65a-7e4a-4ab1-9c62-772b416ca9e9.json) |
| v2-typescript-safe-06 | completed | completed | matches_proposed_labels | [Report](reports/v2-typescript-safe-06-9ae3225f-294d-48c7-aa94-573c4f2406ae.json) |
| v2-typescript-vulnerable-01 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-typescript-vulnerable-01-68d9aa65-dd57-4a30-91d1-742f6fadeb64.json) |
| v2-typescript-vulnerable-02 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-typescript-vulnerable-02-aa7a1dd7-4b4f-425c-ad0d-89e4b192b45b.json) |
| v2-typescript-vulnerable-03 | completed | completed | expected_not_observed | [Report](reports/v2-typescript-vulnerable-03-06284213-19c8-49c7-be52-762aa7e8894f.json) |
| v2-typescript-vulnerable-04 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-typescript-vulnerable-04-72cf49d4-0fc9-4acf-adaa-a4e0626e94d9.json) |
| v2-typescript-vulnerable-05 | completed | completed | expected_not_observed | [Report](reports/v2-typescript-vulnerable-05-bdfd93ef-a9d1-419e-a037-4a3dadd93970.json) |
| v2-typescript-vulnerable-06 | completed | completed | expected_not_observed | [Report](reports/v2-typescript-vulnerable-06-47ec345b-74cb-451d-8f72-0ee15f436c62.json) |
| v2-visualbasic-safe-01 | completed | completed | matches_proposed_labels | [Report](reports/v2-visualbasic-safe-01-724b502f-5fc3-4d4d-9940-d72f24e88c2b.json) |
| v2-visualbasic-safe-02 | completed | completed | unexpected_findings | [Report](reports/v2-visualbasic-safe-02-73fb50df-fc29-48a1-b696-1015b7893e32.json) |
| v2-visualbasic-safe-03 | completed | completed | matches_proposed_labels | [Report](reports/v2-visualbasic-safe-03-12800ab0-f125-4a1d-a890-eac3b0ec3c8f.json) |
| v2-visualbasic-safe-04 | completed | completed | matches_proposed_labels | [Report](reports/v2-visualbasic-safe-04-e0c6a240-1dbe-4f53-b175-87f84ba60e6a.json) |
| v2-visualbasic-safe-05 | completed | completed | matches_proposed_labels | [Report](reports/v2-visualbasic-safe-05-c94fe8df-7a9e-41a3-bdff-a65c9b4bf800.json) |
| v2-visualbasic-safe-06 | completed | completed | matches_proposed_labels | [Report](reports/v2-visualbasic-safe-06-9dde4007-a8f5-4c69-af81-fad73fd37370.json) |
| v2-visualbasic-vulnerable-01 | completed | completed | expected_not_observed | [Report](reports/v2-visualbasic-vulnerable-01-20af3c9e-bfb9-4abd-bbee-c48079134477.json) |
| v2-visualbasic-vulnerable-02 | completed | completed | expected_not_observed | [Report](reports/v2-visualbasic-vulnerable-02-31611194-4835-4e94-9614-3b8f14a6a058.json) |
| v2-visualbasic-vulnerable-03 | completed | completed | expected_not_observed | [Report](reports/v2-visualbasic-vulnerable-03-382aba9d-69d1-4706-9188-743312126cf9.json) |
| v2-visualbasic-vulnerable-04 | completed | completed | expected_not_observed | [Report](reports/v2-visualbasic-vulnerable-04-c0ba3975-5f54-49bc-aa83-c9fcc64041c1.json) |
| v2-visualbasic-vulnerable-05 | completed | completed | expected_not_observed | [Report](reports/v2-visualbasic-vulnerable-05-2bf986cf-1cee-45fd-a0e5-0c4e8d24d63b.json) |
| v2-visualbasic-vulnerable-06 | completed | completed | expected_not_observed | [Report](reports/v2-visualbasic-vulnerable-06-ae4ff672-8781-45f4-916a-6e601ac926a1.json) |

## Incomplete checks

- **v2-bash-safe-01**: Scan did not complete successfully; bin/thumbnail-mode.sh: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-bash-safe-02**: Scan did not complete successfully; bin/check-service.sh: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-bash-safe-03**: Scan did not complete successfully; bin/list-artifacts.sh: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-bash-safe-04**: Scan did not complete successfully; bin/batch-window.sh: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-bash-safe-05**: Scan did not complete successfully; bin/read-theme.sh: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-bash-safe-06**: Scan did not complete successfully; bin/check-local-digest.sh: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-bash-vulnerable-01**: Scan did not complete successfully; bin/dispatch-job.sh: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-bash-vulnerable-02**: Scan did not complete successfully; bin/export-tags.sh: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-bash-vulnerable-03**: Scan did not complete successfully; bin/remote-ticket.sh: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-bash-vulnerable-04**: Scan did not complete successfully; bin/fetch-inventory.sh: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-bash-vulnerable-05**: Scan did not complete successfully; bin/status-banner.sh: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-bash-vulnerable-06**: Scan did not complete successfully; bin/certificate-days.sh: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-c-safe-04**: Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage; src/event_queue.c: no complete trusted-parser/check outcome
- **v2-go-vulnerable-01**: Scan did not complete successfully; search.go: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-java-safe-05**: HelpResources.java: no complete trusted-parser/check outcome; Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-java-vulnerable-01**: LabelSearch.java: no complete trusted-parser/check outcome; Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-kotlin-safe-01**: AuditBatch.kt: no complete trusted-parser/check outcome; Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-kotlin-safe-03**: Scan did not complete successfully; TelemetryReader.kt: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-kotlin-safe-05**: LineLocator.kt: no complete trusted-parser/check outcome; Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-kotlin-vulnerable-01**: ReportController.kt: no complete trusted-parser/check outcome; Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-kotlin-vulnerable-03**: Provisioning.kt: no complete trusted-parser/check outcome; Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-kotlin-vulnerable-04**: ExportRoute.kt: no complete trusted-parser/check outcome; Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-kotlin-vulnerable-06**: BackupForm.kt: no complete trusted-parser/check outcome; Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-python-safe-01**: Scan did not complete successfully; directory.py: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-python-safe-03**: Scan did not complete successfully; geocode.py: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-python-safe-05**: Scan did not complete successfully; checkpoint.py: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-python-vulnerable-01**: Scan did not complete successfully; export.py: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-python-vulnerable-02**: Scan did not complete successfully; preview.py: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-python-vulnerable-04**: Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage; thumbnail.py: no complete trusted-parser/check outcome
- **v2-python-vulnerable-05**: Scan did not complete successfully; resume.py: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-python-vulnerable-06**: Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage; telemetry.py: no complete trusted-parser/check outcome
- **v2-rust-safe-03**: Scan did not complete successfully; bookmark.rs: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-rust-vulnerable-03**: Scan did not complete successfully; channel.rs: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-swift-safe-01**: NoteTitle.swift: no complete trusted-parser/check outcome; Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-swift-safe-02**: Scan did not complete successfully; ShortcutPreferences.swift: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-swift-safe-03**: DocumentSearch.swift: no complete trusted-parser/check outcome; Scan did not complete successfully; SearchSelection.swift: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-swift-safe-04**: HolidayCalendar.swift: no complete trusted-parser/check outcome; Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-swift-safe-05**: ImageMetadata.swift: no complete trusted-parser/check outcome; OpenPanelAction.swift: no complete trusted-parser/check outcome; Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-swift-safe-06**: ColorPreference.swift: no complete trusted-parser/check outcome; Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-swift-vulnerable-01**: LicenseService.swift: no complete trusted-parser/check outcome; Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-swift-vulnerable-02**: Scan did not complete successfully; SupportUpload.swift: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-swift-vulnerable-03**: Scan did not complete successfully; SketchImport.swift: no complete trusted-parser/check outcome; SketchViewModel.swift: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-swift-vulnerable-04**: ReceiptTags.swift: no complete trusted-parser/check outcome; Scan did not complete successfully; TagAction.swift: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-swift-vulnerable-05**: DesignDisplay.swift: no complete trusted-parser/check outcome; DesignGate.swift: no complete trusted-parser/check outcome; Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-swift-vulnerable-06**: ReportManifest.swift: no complete trusted-parser/check outcome; ReportRenderer.swift: no complete trusted-parser/check outcome; Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-typescript-safe-04**: Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage; workflow.ts: no complete trusted-parser/check outcome
- **v2-typescript-vulnerable-01**: Scan did not complete successfully; print.ts: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-typescript-vulnerable-02**: Scan did not complete successfully; mail-digest.ts: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-typescript-vulnerable-04**: Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage; transform.ts: no complete trusted-parser/check outcome

A missed expected finding is a detection observation, not permission to relabel or tune a held-out case. Unexpected findings require independent semantic review. Parse/check failures stay incomplete; they must not count as safe results. The full journal retains source/specification hashes, exact reports, tool coverage and prior attempts.
