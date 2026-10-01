# Candidate static-validation evidence

These are trusted scanner observations against AI-authored, unapproved labels. They are not a quality benchmark, human approval, or runtime test.

Recorded cases: **204/204**. Model calls: **0**. Human approvals created: **0**.

## Frozen environment

```json
{
  "profile": "security-v2",
  "profile_digests": {
    "source": "addb5891684c529093e5e3dbb181becb30ba3db4909989a95666609a2fbd076e",
    "dependency": "b2a78d8167fb4b467bc3674bccf022ff4ed6923e17e86ffa68b5921f4312644b"
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
| v2-bash-safe-01 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-bash-safe-01-6a6847ca-8540-4ba3-9bb9-0f2ecfbed0d7.json) |
| v2-bash-safe-02 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-bash-safe-02-5829ef2a-7a62-4ff5-a47d-df8024833842.json) |
| v2-bash-safe-03 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-bash-safe-03-3a34d937-5d4e-4e66-a271-df7979974ed2.json) |
| v2-bash-safe-04 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-bash-safe-04-cbbfaa83-8b43-4b77-aa99-da9c687874d1.json) |
| v2-bash-safe-05 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-bash-safe-05-d68f3c0f-ef91-4029-829f-3b77935c228a.json) |
| v2-bash-safe-06 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-bash-safe-06-827e73b6-d4c8-4bb2-9977-11144dd76bfa.json) |
| v2-bash-vulnerable-01 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-bash-vulnerable-01-1c72bae3-95a6-4ce6-9d9f-2d7b5689f817.json) |
| v2-bash-vulnerable-02 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-bash-vulnerable-02-6a6294d3-7902-4ce0-bd8e-e550cd7cbd94.json) |
| v2-bash-vulnerable-03 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-bash-vulnerable-03-b0adf498-e2d0-46ac-879c-42cae4a9f81e.json) |
| v2-bash-vulnerable-04 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-bash-vulnerable-04-3e8d0fb1-4b6a-4597-a5b5-4a4fac3df93d.json) |
| v2-bash-vulnerable-05 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-bash-vulnerable-05-2903bfb9-655c-43b8-964f-6103eb8f6b21.json) |
| v2-bash-vulnerable-06 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-bash-vulnerable-06-6999f872-df27-48f8-9e92-11dfda418955.json) |
| v2-c-safe-01 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-c-safe-01-a9d1db8c-42c8-4e8a-bb92-a29a3ebf0861.json) |
| v2-c-safe-02 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-c-safe-02-f34e6252-8b0a-4eb2-83db-09d61acad305.json) |
| v2-c-safe-03 | completed | completed | matches_proposed_labels | [Report](reports/v2-c-safe-03-0889fbb4-49da-4e46-bcfc-e9e0a4fd0d33.json) |
| v2-c-safe-04 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-c-safe-04-9ab78015-2635-4782-9b7a-13f3b7bc9ea7.json) |
| v2-c-safe-05 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-c-safe-05-9d02c322-a88f-4383-bd1b-32df5910674d.json) |
| v2-c-safe-06 | completed | completed | matches_proposed_labels | [Report](reports/v2-c-safe-06-726726d2-dc0d-4a1b-8bd7-528210828bda.json) |
| v2-c-vulnerable-01 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-c-vulnerable-01-6d6b3aa2-e074-4f9d-bd5a-c682bf41ff16.json) |
| v2-c-vulnerable-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-c-vulnerable-02-420289f0-b25d-427b-b3fe-ac5268d5591f.json) |
| v2-c-vulnerable-03 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-c-vulnerable-03-adac5ad7-79c0-4e27-965b-ef63cbbe31eb.json) |
| v2-c-vulnerable-04 | completed | completed | expected_not_observed | [Report](reports/v2-c-vulnerable-04-eeb92cf4-1060-48ec-817c-25be00894647.json) |
| v2-c-vulnerable-05 | completed | completed | matches_proposed_labels | [Report](reports/v2-c-vulnerable-05-ceee125d-9505-4e20-9460-edb031f6129d.json) |
| v2-c-vulnerable-06 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-c-vulnerable-06-f81a6a0e-937a-40c3-93ad-a3b1759ba626.json) |
| v2-cpp-safe-01 | completed | completed | matches_proposed_labels | [Report](reports/v2-cpp-safe-01-eb39853f-60e7-436c-a15a-8a604ec74903.json) |
| v2-cpp-safe-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-cpp-safe-02-2016214d-9b9f-4ca2-9292-e1a7dfd114c2.json) |
| v2-cpp-safe-03 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-cpp-safe-03-f75fefd5-f827-44c1-8c95-62f98dba25c5.json) |
| v2-cpp-safe-04 | completed | completed | matches_proposed_labels | [Report](reports/v2-cpp-safe-04-e1ead399-f519-4556-b40e-979826b93e7b.json) |
| v2-cpp-safe-05 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-cpp-safe-05-b292ae69-a130-4cfd-94d3-39beee33ec38.json) |
| v2-cpp-safe-06 | completed | completed | matches_proposed_labels | [Report](reports/v2-cpp-safe-06-48d9e8d4-2b67-43f8-a09b-bbb545c50825.json) |
| v2-cpp-vulnerable-01 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-cpp-vulnerable-01-bac6fef7-c386-4ba1-8dc7-d027da1a97a9.json) |
| v2-cpp-vulnerable-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-cpp-vulnerable-02-e6eb0a0d-29ef-4075-8c31-c1127a66da6e.json) |
| v2-cpp-vulnerable-03 | completed | completed | expected_not_observed | [Report](reports/v2-cpp-vulnerable-03-54ac751e-17c6-4662-8d21-a1086b170048.json) |
| v2-cpp-vulnerable-04 | completed | completed | expected_not_observed | [Report](reports/v2-cpp-vulnerable-04-e43cd0d4-0eae-4813-adc1-d4ff184cc225.json) |
| v2-cpp-vulnerable-05 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-cpp-vulnerable-05-fce9dd8f-1217-47b6-8f79-080428ad308d.json) |
| v2-cpp-vulnerable-06 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-cpp-vulnerable-06-f68603f8-4afe-4f65-912c-5692891d625d.json) |
| v2-csharp-safe-01 | completed | completed | matches_proposed_labels | [Report](reports/v2-csharp-safe-01-4e8caafe-e7bc-498a-9974-6b980117f4e0.json) |
| v2-csharp-safe-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-csharp-safe-02-bbbaad31-4bd9-4fb3-8984-14d951b24d86.json) |
| v2-csharp-safe-03 | completed | completed | matches_proposed_labels | [Report](reports/v2-csharp-safe-03-3ffba79d-dc60-461f-bc14-9b1835d809e1.json) |
| v2-csharp-safe-04 | completed | completed | matches_proposed_labels | [Report](reports/v2-csharp-safe-04-0e5627cf-52e1-48eb-a259-dd766559c45c.json) |
| v2-csharp-safe-05 | completed | completed | matches_proposed_labels | [Report](reports/v2-csharp-safe-05-c975ecb8-75ee-4fa6-9a48-91af3662b665.json) |
| v2-csharp-safe-06 | completed | completed | matches_proposed_labels | [Report](reports/v2-csharp-safe-06-0bb1a23b-fda9-4f8b-a5c5-0dcd671bfe81.json) |
| v2-csharp-vulnerable-01 | completed | completed | expected_not_observed | [Report](reports/v2-csharp-vulnerable-01-0a0afca4-4ae2-4148-8743-d40cac0f3e17.json) |
| v2-csharp-vulnerable-02 | completed | completed | expected_not_observed | [Report](reports/v2-csharp-vulnerable-02-eca50e05-9b59-4509-871b-533a4a79ce00.json) |
| v2-csharp-vulnerable-03 | completed | completed | expected_not_observed | [Report](reports/v2-csharp-vulnerable-03-840da841-8449-4de6-979b-ab2e85f23093.json) |
| v2-csharp-vulnerable-04 | completed | completed | matches_proposed_labels | [Report](reports/v2-csharp-vulnerable-04-256c93ca-1295-4f12-91a0-dc2f64df2a24.json) |
| v2-csharp-vulnerable-05 | completed | completed | matches_proposed_labels | [Report](reports/v2-csharp-vulnerable-05-22c1f555-dde0-4e41-9388-e45ed479902c.json) |
| v2-csharp-vulnerable-06 | completed | completed | matches_proposed_labels | [Report](reports/v2-csharp-vulnerable-06-6ee3c6b4-7066-4b95-ad33-61c758b3e872.json) |
| v2-fsharp-safe-01 | completed | completed | matches_proposed_labels | [Report](reports/v2-fsharp-safe-01-37619b04-3c0a-4d55-bbe1-2fc4369058c1.json) |
| v2-fsharp-safe-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-fsharp-safe-02-b6b38f37-33c9-46b2-b072-0439d4fbf69e.json) |
| v2-fsharp-safe-03 | completed | completed | matches_proposed_labels | [Report](reports/v2-fsharp-safe-03-8a72e252-77ca-48c7-8a5f-53c69086232a.json) |
| v2-fsharp-safe-04 | completed | completed | matches_proposed_labels | [Report](reports/v2-fsharp-safe-04-5fa6983c-cf03-4f25-bf2a-f6786450512c.json) |
| v2-fsharp-safe-05 | completed | completed | matches_proposed_labels | [Report](reports/v2-fsharp-safe-05-453c8f9b-19de-47e5-87ed-ccdb5e94b6de.json) |
| v2-fsharp-safe-06 | completed | completed | matches_proposed_labels | [Report](reports/v2-fsharp-safe-06-72af5f93-e0af-4f11-9f47-72103dc79ea2.json) |
| v2-fsharp-vulnerable-01 | completed | completed | expected_not_observed | [Report](reports/v2-fsharp-vulnerable-01-7c1243c9-8947-49d7-a745-23666b5804d7.json) |
| v2-fsharp-vulnerable-02 | completed | completed | expected_not_observed | [Report](reports/v2-fsharp-vulnerable-02-257f40bb-2df0-43f0-91ac-e7992d371060.json) |
| v2-fsharp-vulnerable-03 | completed | completed | unexpected_findings | [Report](reports/v2-fsharp-vulnerable-03-e13d0af0-0168-4ae0-9a77-4286d40cec49.json) |
| v2-fsharp-vulnerable-04 | completed | completed | missing_and_unexpected | [Report](reports/v2-fsharp-vulnerable-04-8cf55c8f-ef47-4824-9bb0-8ce59ecd69a1.json) |
| v2-fsharp-vulnerable-05 | completed | completed | expected_not_observed | [Report](reports/v2-fsharp-vulnerable-05-ffd17d98-8427-47f4-aed3-784157029fa7.json) |
| v2-fsharp-vulnerable-06 | completed | completed | expected_not_observed | [Report](reports/v2-fsharp-vulnerable-06-f4ccb36e-a20e-4f8d-b485-c7035a09953f.json) |
| v2-go-safe-01 | completed | completed | matches_proposed_labels | [Report](reports/v2-go-safe-01-35915156-8e46-4f12-b771-5fd909979a8d.json) |
| v2-go-safe-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-go-safe-02-8f670e83-cae1-4503-bff1-90be6b0ca43c.json) |
| v2-go-safe-03 | completed | completed | matches_proposed_labels | [Report](reports/v2-go-safe-03-9be16e35-8ebb-4dba-b47c-7602cb0d92b8.json) |
| v2-go-safe-04 | completed | completed | matches_proposed_labels | [Report](reports/v2-go-safe-04-6ee8a703-2767-4b5c-8401-cb628a64f967.json) |
| v2-go-safe-05 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-go-safe-05-b707c3b5-3b16-478b-a1fd-5ec37a2d4be4.json) |
| v2-go-safe-06 | completed | completed | matches_proposed_labels | [Report](reports/v2-go-safe-06-1a83a9d0-430c-4f18-a928-faea73df4531.json) |
| v2-go-vulnerable-01 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-go-vulnerable-01-dfb90b8e-650b-44f6-a279-c38c79a3267f.json) |
| v2-go-vulnerable-02 | completed | completed | expected_not_observed | [Report](reports/v2-go-vulnerable-02-7c7ae9fb-9d21-4bdd-844a-dc3fefe2c7c9.json) |
| v2-go-vulnerable-03 | completed | completed | expected_not_observed | [Report](reports/v2-go-vulnerable-03-ef90b6f3-8dd0-48d1-b368-3d259b8829c5.json) |
| v2-go-vulnerable-04 | completed | completed | expected_not_observed | [Report](reports/v2-go-vulnerable-04-27566755-01a8-4d57-acf8-438d2469b17f.json) |
| v2-go-vulnerable-05 | completed | completed | expected_not_observed | [Report](reports/v2-go-vulnerable-05-81b2e7ec-22f8-4297-baf2-c8bcd71ce23e.json) |
| v2-go-vulnerable-06 | completed | completed | expected_not_observed | [Report](reports/v2-go-vulnerable-06-6d806439-525a-49ca-86fa-24d23d254491.json) |
| v2-java-safe-01 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-java-safe-01-243d391d-e9b8-43f8-a3b1-317c3c165898.json) |
| v2-java-safe-02 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-java-safe-02-d987e888-b17a-430e-a406-4c4aeae0ca41.json) |
| v2-java-safe-03 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-java-safe-03-c7708c8f-29a2-4d6b-a398-f4e680237c71.json) |
| v2-java-safe-04 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-java-safe-04-041330a0-1e41-41f6-8a15-a42a3e3d4b3f.json) |
| v2-java-safe-05 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-java-safe-05-13e4776f-a820-4b33-bd1b-4a2d0cbf341f.json) |
| v2-java-safe-06 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-java-safe-06-214a2ee2-3b65-4f29-aaf9-2f9e1807eccf.json) |
| v2-java-vulnerable-01 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-java-vulnerable-01-97d7f4d5-a754-4cad-aa8d-c502eda08f13.json) |
| v2-java-vulnerable-02 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-java-vulnerable-02-522abbae-b062-4652-a282-e7251a1f4dd9.json) |
| v2-java-vulnerable-03 | completed | completed | expected_not_observed | [Report](reports/v2-java-vulnerable-03-521f0943-75dc-4710-b388-f369404a15b3.json) |
| v2-java-vulnerable-04 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-java-vulnerable-04-5f290985-e4b5-4e2a-bdca-0ad42ee081e1.json) |
| v2-java-vulnerable-05 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-java-vulnerable-05-14f04f84-fd7c-4e2f-b32d-f37d128702cd.json) |
| v2-java-vulnerable-06 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-java-vulnerable-06-aa306907-271e-4413-aac2-cd4f0770d4fd.json) |
| v2-javascript-safe-01 | completed | completed | matches_proposed_labels | [Report](reports/v2-javascript-safe-01-a4fda9b5-b821-4543-8aa4-5f149e0ae182.json) |
| v2-javascript-safe-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-javascript-safe-02-0c85b77e-ad67-4827-a31e-a456d6c1c485.json) |
| v2-javascript-safe-03 | completed | completed | matches_proposed_labels | [Report](reports/v2-javascript-safe-03-4ee3a789-d1d4-42b4-a54b-ee81af0aca59.json) |
| v2-javascript-safe-04 | completed | completed | matches_proposed_labels | [Report](reports/v2-javascript-safe-04-a1c00e03-4a0a-4e61-8301-4f0c3f3e8ed8.json) |
| v2-javascript-safe-05 | completed | completed | matches_proposed_labels | [Report](reports/v2-javascript-safe-05-3b9b0cf9-81f1-47db-a2af-cbda881b7868.json) |
| v2-javascript-safe-06 | completed | completed | matches_proposed_labels | [Report](reports/v2-javascript-safe-06-bbc57d52-2ec6-4c51-9226-80b6f1057ac0.json) |
| v2-javascript-vulnerable-01 | completed | completed | expected_not_observed | [Report](reports/v2-javascript-vulnerable-01-bc7ff6f7-38a5-47b0-a335-4b070ce7729d.json) |
| v2-javascript-vulnerable-02 | completed | completed | expected_not_observed | [Report](reports/v2-javascript-vulnerable-02-e2d04875-78c7-40cf-8571-21cae0c7a076.json) |
| v2-javascript-vulnerable-03 | completed | completed | expected_not_observed | [Report](reports/v2-javascript-vulnerable-03-17b28234-4a35-4036-811d-f48a31995dcf.json) |
| v2-javascript-vulnerable-04 | completed | completed | expected_not_observed | [Report](reports/v2-javascript-vulnerable-04-8b118581-fdf3-409f-834f-6f5eac27f17b.json) |
| v2-javascript-vulnerable-05 | completed | completed | expected_not_observed | [Report](reports/v2-javascript-vulnerable-05-7ef9351c-7e40-467e-8724-8254af2c36a4.json) |
| v2-javascript-vulnerable-06 | completed | completed | expected_not_observed | [Report](reports/v2-javascript-vulnerable-06-2669624c-5000-471e-aeec-d617cf7526cd.json) |
| v2-kotlin-safe-01 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-kotlin-safe-01-e437d87e-e2e5-483a-ba12-57db30b4fc47.json) |
| v2-kotlin-safe-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-kotlin-safe-02-2e9129d2-df55-4d66-a40f-c7ba7e94b91e.json) |
| v2-kotlin-safe-03 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-kotlin-safe-03-cacd2370-4ffe-43de-9d5d-a1dd492ec6e3.json) |
| v2-kotlin-safe-04 | completed | completed | unexpected_findings | [Report](reports/v2-kotlin-safe-04-47bb2d66-f84e-4a97-a49d-94e5f7fab582.json) |
| v2-kotlin-safe-05 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-kotlin-safe-05-253f2aee-a291-492f-96c3-7f6d9205252a.json) |
| v2-kotlin-safe-06 | completed | completed | matches_proposed_labels | [Report](reports/v2-kotlin-safe-06-9b5a4c58-40f5-420b-b8ad-bfeef678d0e7.json) |
| v2-kotlin-vulnerable-01 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-kotlin-vulnerable-01-f6f0867b-47f6-4f0a-b002-dfdd2163a647.json) |
| v2-kotlin-vulnerable-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-kotlin-vulnerable-02-ebd13345-45ec-47f2-98dc-6a0e37cf3441.json) |
| v2-kotlin-vulnerable-03 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-kotlin-vulnerable-03-8048fcd4-12ff-4f63-af76-58271baab6ee.json) |
| v2-kotlin-vulnerable-04 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-kotlin-vulnerable-04-e385d5e3-57df-4779-99c3-9104a9a08de3.json) |
| v2-kotlin-vulnerable-05 | completed | completed | expected_not_observed | [Report](reports/v2-kotlin-vulnerable-05-ee63ef15-cf43-43e8-8b19-fcc57bf582aa.json) |
| v2-kotlin-vulnerable-06 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-kotlin-vulnerable-06-5a04d848-b2c1-41ae-bb60-884efa6d107d.json) |
| v2-php-safe-01 | completed | completed | matches_proposed_labels | [Report](reports/v2-php-safe-01-25ade97b-b370-4e1c-a4f8-45ce9b974b33.json) |
| v2-php-safe-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-php-safe-02-b398a3dd-a3dd-49ef-8d29-60e59c975b40.json) |
| v2-php-safe-03 | completed | completed | matches_proposed_labels | [Report](reports/v2-php-safe-03-1447674c-530c-412e-973e-69fa986cd206.json) |
| v2-php-safe-04 | completed | completed | matches_proposed_labels | [Report](reports/v2-php-safe-04-46878737-75e1-4994-9ac3-3a7de5fb016e.json) |
| v2-php-safe-05 | completed | completed | matches_proposed_labels | [Report](reports/v2-php-safe-05-b203d87d-b8e1-4924-8810-db8877710b95.json) |
| v2-php-safe-06 | completed | completed | matches_proposed_labels | [Report](reports/v2-php-safe-06-ff987c3a-f21b-4792-a57d-a6d60526441c.json) |
| v2-php-vulnerable-01 | completed | completed | expected_not_observed | [Report](reports/v2-php-vulnerable-01-e38c724b-d4f7-45a5-99ac-fb39f61b152f.json) |
| v2-php-vulnerable-02 | completed | completed | expected_not_observed | [Report](reports/v2-php-vulnerable-02-710ed757-a2f0-4aaf-90f6-01c735c1532e.json) |
| v2-php-vulnerable-03 | completed | completed | expected_not_observed | [Report](reports/v2-php-vulnerable-03-ab179b0c-1fbc-4178-938f-5c87ba1a13f4.json) |
| v2-php-vulnerable-04 | completed | completed | expected_not_observed | [Report](reports/v2-php-vulnerable-04-3544af55-41b7-40f0-9d12-ee8dbf71629a.json) |
| v2-php-vulnerable-05 | completed | completed | matches_proposed_labels | [Report](reports/v2-php-vulnerable-05-201495a8-43a5-4d08-81fa-958059fd8d44.json) |
| v2-php-vulnerable-06 | completed | completed | expected_not_observed | [Report](reports/v2-php-vulnerable-06-402a99ed-63d3-4f24-a033-207900417608.json) |
| v2-python-safe-01 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-python-safe-01-7903535f-ed2f-4bcd-ab0c-c8a64f518fbf.json) |
| v2-python-safe-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-python-safe-02-6a2927bf-7a10-489a-b0c8-e96b72f67575.json) |
| v2-python-safe-03 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-python-safe-03-ef5fa860-2d5f-4712-85f1-009eea7c3112.json) |
| v2-python-safe-04 | completed | completed | unexpected_findings | [Report](reports/v2-python-safe-04-a22dc06b-2a9e-49b1-8830-bcb7dffbab77.json) |
| v2-python-safe-05 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-python-safe-05-b4d91a60-d8d5-4cd0-9a7f-0f64f451221e.json) |
| v2-python-safe-06 | completed | completed | matches_proposed_labels | [Report](reports/v2-python-safe-06-79176d3e-b5d9-4ab6-b634-0d03a5c28156.json) |
| v2-python-vulnerable-01 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-python-vulnerable-01-33c98843-d6bb-4257-bb77-fbd03facf0ab.json) |
| v2-python-vulnerable-02 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-python-vulnerable-02-d3b0c309-1bef-407e-837a-e13fb9204f63.json) |
| v2-python-vulnerable-03 | completed | completed | expected_not_observed | [Report](reports/v2-python-vulnerable-03-556d1d01-f5ba-4e59-a4ef-e76da67734c0.json) |
| v2-python-vulnerable-04 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-python-vulnerable-04-3123a168-320d-454c-8ae2-68c60f0941eb.json) |
| v2-python-vulnerable-05 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-python-vulnerable-05-723cbba6-67b8-4b27-8d5f-b008a93222ca.json) |
| v2-python-vulnerable-06 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-python-vulnerable-06-5e60d88c-e5c8-41a4-86cb-30b163871177.json) |
| v2-ruby-safe-01 | completed | completed | matches_proposed_labels | [Report](reports/v2-ruby-safe-01-010301e6-9811-4c00-9195-d7c4c8365cc2.json) |
| v2-ruby-safe-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-ruby-safe-02-2271eeb8-77fe-4f75-bf71-479fbe0ada24.json) |
| v2-ruby-safe-03 | completed | completed | matches_proposed_labels | [Report](reports/v2-ruby-safe-03-c8b12bdf-3717-4e48-a1ac-91b6cabc1a32.json) |
| v2-ruby-safe-04 | completed | completed | matches_proposed_labels | [Report](reports/v2-ruby-safe-04-b8c1eb3a-bfce-41c0-bdfb-2821f312700d.json) |
| v2-ruby-safe-05 | completed | completed | matches_proposed_labels | [Report](reports/v2-ruby-safe-05-c98d6fcd-e9a0-4c13-885c-5ec159702c3f.json) |
| v2-ruby-safe-06 | completed | completed | matches_proposed_labels | [Report](reports/v2-ruby-safe-06-0a05e713-5020-40e2-afa1-9701d9e06bec.json) |
| v2-ruby-vulnerable-01 | completed | completed | expected_not_observed | [Report](reports/v2-ruby-vulnerable-01-db4c6bd3-9f5b-4591-b948-1b2316f4d979.json) |
| v2-ruby-vulnerable-02 | completed | completed | expected_not_observed | [Report](reports/v2-ruby-vulnerable-02-16058911-8593-4789-b6ff-dbcb38a4b73c.json) |
| v2-ruby-vulnerable-03 | completed | completed | expected_not_observed | [Report](reports/v2-ruby-vulnerable-03-9378e756-f4cd-4045-b4a4-07c65a476b6d.json) |
| v2-ruby-vulnerable-04 | completed | completed | expected_not_observed | [Report](reports/v2-ruby-vulnerable-04-e24b2dba-2960-4128-a128-0f2b2f0af3a1.json) |
| v2-ruby-vulnerable-05 | completed | completed | expected_not_observed | [Report](reports/v2-ruby-vulnerable-05-18f5c79e-b5ca-4036-b801-6db38597ce2d.json) |
| v2-ruby-vulnerable-06 | completed | completed | expected_not_observed | [Report](reports/v2-ruby-vulnerable-06-27f6e19c-3a66-4d4d-b034-9ae5ecbb671d.json) |
| v2-rust-safe-01 | completed | completed | matches_proposed_labels | [Report](reports/v2-rust-safe-01-ab885aad-d8e3-4328-b0ca-a1074a5f88ba.json) |
| v2-rust-safe-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-rust-safe-02-e1aef6aa-2324-4a45-a05d-f1ccf6460c9c.json) |
| v2-rust-safe-03 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-rust-safe-03-0352eabb-85cb-40d0-be09-d6a4098302ff.json) |
| v2-rust-safe-04 | completed | completed | matches_proposed_labels | [Report](reports/v2-rust-safe-04-dd2ab285-d778-4067-b998-d6b418f064d4.json) |
| v2-rust-safe-05 | completed | completed | matches_proposed_labels | [Report](reports/v2-rust-safe-05-f14dc652-9bd8-47f6-8dcd-4c424785f55c.json) |
| v2-rust-safe-06 | completed | completed | matches_proposed_labels | [Report](reports/v2-rust-safe-06-27224b6e-5676-4f34-a389-8301ca1efa62.json) |
| v2-rust-vulnerable-01 | completed | completed | expected_not_observed | [Report](reports/v2-rust-vulnerable-01-0de0f435-a1c0-413a-9aba-5eea039ca134.json) |
| v2-rust-vulnerable-02 | completed | completed | expected_not_observed | [Report](reports/v2-rust-vulnerable-02-cd222c19-a156-4389-8c83-10e239f081c5.json) |
| v2-rust-vulnerable-03 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-rust-vulnerable-03-8e20ef24-34b2-4593-a4fd-e48f55c52fac.json) |
| v2-rust-vulnerable-04 | completed | completed | matches_proposed_labels | [Report](reports/v2-rust-vulnerable-04-355346d0-8fe4-44a4-845b-343d0d81226b.json) |
| v2-rust-vulnerable-05 | completed | completed | expected_not_observed | [Report](reports/v2-rust-vulnerable-05-76716c31-1121-47fa-90df-a76f9ec3fc79.json) |
| v2-rust-vulnerable-06 | completed | completed | expected_not_observed | [Report](reports/v2-rust-vulnerable-06-75c6df2b-f024-428f-9ae3-4168133b984e.json) |
| v2-scala-safe-01 | completed | completed | matches_proposed_labels | [Report](reports/v2-scala-safe-01-61ba0493-da66-47f7-879b-53a87aeeb886.json) |
| v2-scala-safe-02 | completed | completed | matches_proposed_labels | [Report](reports/v2-scala-safe-02-b2df60ea-8c5c-49e5-a23d-683d1ddc43d9.json) |
| v2-scala-safe-03 | completed | completed | matches_proposed_labels | [Report](reports/v2-scala-safe-03-dceef88f-61b8-46b1-880e-3c71a1ae3abf.json) |
| v2-scala-safe-04 | completed | completed | matches_proposed_labels | [Report](reports/v2-scala-safe-04-d8803017-8e6f-4cc4-be7b-dd7b35cd9258.json) |
| v2-scala-safe-05 | completed | completed | matches_proposed_labels | [Report](reports/v2-scala-safe-05-45cd2e72-202f-4a63-92da-efdd529dbbd7.json) |
| v2-scala-safe-06 | completed | completed | matches_proposed_labels | [Report](reports/v2-scala-safe-06-5d84a5d7-2fb7-44aa-814b-0fecb8e43185.json) |
| v2-scala-vulnerable-01 | completed | completed | expected_not_observed | [Report](reports/v2-scala-vulnerable-01-1c6322be-ea61-4a98-95f0-3bf3afbd92b7.json) |
| v2-scala-vulnerable-02 | completed | completed | expected_not_observed | [Report](reports/v2-scala-vulnerable-02-ad6d85de-6377-48b2-831b-60f89266bb4d.json) |
| v2-scala-vulnerable-03 | completed | completed | expected_not_observed | [Report](reports/v2-scala-vulnerable-03-fe8e4eab-8fd7-4c66-91d3-3ec26cdc8b81.json) |
| v2-scala-vulnerable-04 | completed | completed | expected_not_observed | [Report](reports/v2-scala-vulnerable-04-9c37105e-7d41-4238-99fc-8498005d95d2.json) |
| v2-scala-vulnerable-05 | completed | completed | expected_not_observed | [Report](reports/v2-scala-vulnerable-05-f298edb5-934b-4e7f-b380-9d8e08a2bb9e.json) |
| v2-scala-vulnerable-06 | completed | completed | expected_not_observed | [Report](reports/v2-scala-vulnerable-06-1254942d-fd84-4238-af02-d00023361c6f.json) |
| v2-swift-safe-01 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-swift-safe-01-1724fd2c-89ad-44fb-9d86-f1ff71d0839a.json) |
| v2-swift-safe-02 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-swift-safe-02-83d3645b-1b36-4e8b-b484-28b1f4280c9b.json) |
| v2-swift-safe-03 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-swift-safe-03-a4a0272f-3da9-4d91-a436-9ac1ca6ad8e3.json) |
| v2-swift-safe-04 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-swift-safe-04-8b8167c3-ebbf-4c99-a625-f413c46e90f5.json) |
| v2-swift-safe-05 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-swift-safe-05-5b49cb52-eb41-435b-884b-1f549428e680.json) |
| v2-swift-safe-06 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-swift-safe-06-de0176a2-d587-49c2-9ae2-10dea46216b1.json) |
| v2-swift-vulnerable-01 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-swift-vulnerable-01-f59c6d78-d09f-4f3f-a7f7-6f447b6548db.json) |
| v2-swift-vulnerable-02 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-swift-vulnerable-02-fc80f9cd-b893-482b-bc7a-0db6e6739668.json) |
| v2-swift-vulnerable-03 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-swift-vulnerable-03-e8307bac-de11-4ba7-b654-6f85c78a4c64.json) |
| v2-swift-vulnerable-04 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-swift-vulnerable-04-05ff8c43-5b15-4b7f-972c-d95ed54b675a.json) |
| v2-swift-vulnerable-05 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-swift-vulnerable-05-1b7349d5-27c2-4de6-9bb0-5181ddc4667d.json) |
| v2-swift-vulnerable-06 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-swift-vulnerable-06-6dd3ece6-9b6b-4174-a15b-40cd926decde.json) |
| v2-typescript-safe-01 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-typescript-safe-01-10d32f09-fef4-4755-a14c-4db798e0bf54.json) |
| v2-typescript-safe-02 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-typescript-safe-02-9354d325-d3cc-482e-a309-05fe420bdb66.json) |
| v2-typescript-safe-03 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-typescript-safe-03-fdf05f7a-4393-442b-8aec-746801c009d3.json) |
| v2-typescript-safe-04 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-typescript-safe-04-1060ff5a-8e64-47d8-87e5-1a19bb724c43.json) |
| v2-typescript-safe-05 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-typescript-safe-05-a0a17cff-e3a9-4468-afa2-5aa007905c71.json) |
| v2-typescript-safe-06 | incomplete | incomplete | matches_proposed_labels | [Report](reports/v2-typescript-safe-06-266638d5-6db5-4ee2-b84c-4479fd8bb74c.json) |
| v2-typescript-vulnerable-01 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-typescript-vulnerable-01-040a2228-f3fd-4338-a2a9-71e2417e1d35.json) |
| v2-typescript-vulnerable-02 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-typescript-vulnerable-02-ec2be318-a5db-4ba7-a0a3-9930740e66cb.json) |
| v2-typescript-vulnerable-03 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-typescript-vulnerable-03-80a37bc3-f738-4eb5-9018-5320444cc0bb.json) |
| v2-typescript-vulnerable-04 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-typescript-vulnerable-04-01971e86-3fb5-44da-93be-660ec4e51e0b.json) |
| v2-typescript-vulnerable-05 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-typescript-vulnerable-05-827fdcce-4003-4f9f-b898-e008bc4e1a69.json) |
| v2-typescript-vulnerable-06 | incomplete | incomplete | expected_not_observed | [Report](reports/v2-typescript-vulnerable-06-9714b03f-cac5-491d-aca6-15fec2245010.json) |
| v2-visualbasic-safe-01 | completed | completed | matches_proposed_labels | [Report](reports/v2-visualbasic-safe-01-22fa9ee7-ac1c-4e66-8115-73674096197b.json) |
| v2-visualbasic-safe-02 | completed | completed | unexpected_findings | [Report](reports/v2-visualbasic-safe-02-cb7c6c0b-0407-4a4b-8f1b-9e1710b2400a.json) |
| v2-visualbasic-safe-03 | completed | completed | matches_proposed_labels | [Report](reports/v2-visualbasic-safe-03-ccb842d0-5431-4691-9208-7bdb36a2cb7e.json) |
| v2-visualbasic-safe-04 | completed | completed | matches_proposed_labels | [Report](reports/v2-visualbasic-safe-04-7cc6586b-010f-4a0b-b1e5-ddcf92271729.json) |
| v2-visualbasic-safe-05 | completed | completed | matches_proposed_labels | [Report](reports/v2-visualbasic-safe-05-b3e27805-4f67-41ae-a26d-781259d612a9.json) |
| v2-visualbasic-safe-06 | completed | completed | matches_proposed_labels | [Report](reports/v2-visualbasic-safe-06-6fcc39bb-8570-43e6-85a8-f1b3163bcda5.json) |
| v2-visualbasic-vulnerable-01 | completed | completed | expected_not_observed | [Report](reports/v2-visualbasic-vulnerable-01-4c7c4a03-a992-4da3-8a05-9ebc3380d46b.json) |
| v2-visualbasic-vulnerable-02 | completed | completed | expected_not_observed | [Report](reports/v2-visualbasic-vulnerable-02-6f292b39-2799-4706-8599-986c1fba165e.json) |
| v2-visualbasic-vulnerable-03 | completed | completed | expected_not_observed | [Report](reports/v2-visualbasic-vulnerable-03-dddfaa93-82f9-4227-a8b9-1b2bcb22ea5a.json) |
| v2-visualbasic-vulnerable-04 | completed | completed | expected_not_observed | [Report](reports/v2-visualbasic-vulnerable-04-e3a561dc-74bb-4e4b-b44c-e3941d9d241b.json) |
| v2-visualbasic-vulnerable-05 | completed | completed | expected_not_observed | [Report](reports/v2-visualbasic-vulnerable-05-ddbf2240-181d-4cab-8757-1436afbb5de9.json) |
| v2-visualbasic-vulnerable-06 | completed | completed | expected_not_observed | [Report](reports/v2-visualbasic-vulnerable-06-3b4998dc-9c13-4a7d-9ce3-5092cab29a7f.json) |

## Incomplete checks

- **v2-bash-safe-01**: Scan did not complete successfully; Scanned snapshot inventory/hashes differ from the authored source; bin/thumbnail-mode.sh: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete
- **v2-bash-safe-02**: Scan did not complete successfully; Scanned snapshot inventory/hashes differ from the authored source; bin/check-service.sh: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete
- **v2-bash-safe-03**: Scan did not complete successfully; Scanned snapshot inventory/hashes differ from the authored source; bin/list-artifacts.sh: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete
- **v2-bash-safe-04**: Scan did not complete successfully; Scanned snapshot inventory/hashes differ from the authored source; bin/batch-window.sh: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete
- **v2-bash-safe-05**: Scan did not complete successfully; Scanned snapshot inventory/hashes differ from the authored source; bin/read-theme.sh: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete
- **v2-bash-safe-06**: Scan did not complete successfully; Scanned snapshot inventory/hashes differ from the authored source; bin/check-local-digest.sh: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete
- **v2-bash-vulnerable-01**: Scan did not complete successfully; Scanned snapshot inventory/hashes differ from the authored source; bin/dispatch-job.sh: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete
- **v2-bash-vulnerable-02**: Scan did not complete successfully; Scanned snapshot inventory/hashes differ from the authored source; bin/export-tags.sh: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete
- **v2-bash-vulnerable-03**: Scan did not complete successfully; Scanned snapshot inventory/hashes differ from the authored source; bin/remote-ticket.sh: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete
- **v2-bash-vulnerable-04**: Scan did not complete successfully; Scanned snapshot inventory/hashes differ from the authored source; bin/fetch-inventory.sh: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete
- **v2-bash-vulnerable-05**: Scan did not complete successfully; Scanned snapshot inventory/hashes differ from the authored source; bin/status-banner.sh: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete
- **v2-bash-vulnerable-06**: Scan did not complete successfully; Scanned snapshot inventory/hashes differ from the authored source; bin/certificate-days.sh: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete
- **v2-c-safe-01**: Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage; src/hex_identifier.c: no complete trusted-parser/check outcome
- **v2-c-safe-02**: Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage; src/relay_record.c: no complete trusted-parser/check outcome
- **v2-c-safe-04**: Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage; src/event_queue.c: no complete trusted-parser/check outcome
- **v2-c-safe-05**: Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage; src/upload_count.c: no complete trusted-parser/check outcome
- **v2-c-vulnerable-01**: Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage; src/sensor_csv.c: no complete trusted-parser/check outcome
- **v2-c-vulnerable-03**: Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage; src/notice_log.c: no complete trusted-parser/check outcome
- **v2-c-vulnerable-06**: Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage; src/receipt_caption.c: no complete trusted-parser/check outcome
- **v2-cpp-safe-03**: Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage; src/query_plan_view.cpp: no complete trusted-parser/check outcome
- **v2-cpp-safe-05**: Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage; src/sequence_number.cpp: no complete trusted-parser/check outcome
- **v2-cpp-vulnerable-01**: Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage; src/build_status.cpp: no complete trusted-parser/check outcome
- **v2-cpp-vulnerable-05**: Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage; src/retention_job.cpp: no complete trusted-parser/check outcome
- **v2-cpp-vulnerable-06**: Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage; src/PercentSegment.cpp: no complete trusted-parser/check outcome
- **v2-go-safe-05**: Scan did not complete successfully; feed.go: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-go-vulnerable-01**: Scan did not complete successfully; search.go: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-java-safe-01**: MapPage.java: no complete trusted-parser/check outcome; Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-java-safe-02**: QuizReader.java: no complete trusted-parser/check outcome; Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-java-safe-03**: ReleaseVerifier.java: no complete trusted-parser/check outcome; Scan did not complete successfully; Updater.java: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-java-safe-04**: LabelPrinter.java: no complete trusted-parser/check outcome; Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-java-safe-05**: HelpResources.java: no complete trusted-parser/check outcome; Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-java-safe-06**: Scan did not complete successfully; TransitStatus.java: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-java-vulnerable-01**: LabelSearch.java: no complete trusted-parser/check outcome; Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-java-vulnerable-02**: InventoryImport.java: no complete trusted-parser/check outcome; Scan did not complete successfully; UploadController.java: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-java-vulnerable-04**: GatewayClient.java: no complete trusted-parser/check outcome; Scan did not complete successfully; Settlement.java: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-java-vulnerable-05**: LoginService.java: no complete trusted-parser/check outcome; PasswordStore.java: no complete trusted-parser/check outcome; Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-java-vulnerable-06**: CaptionForm.java: no complete trusted-parser/check outcome; Scan did not complete successfully; Watermark.java: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
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
- **v2-typescript-safe-01**: Scan did not complete successfully; checksum.ts: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-typescript-safe-02**: Scan did not complete successfully; archive-member.ts: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-typescript-safe-03**: Scan did not complete successfully; mail-api.ts: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-typescript-safe-04**: Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage; workflow.ts: no complete trusted-parser/check outcome
- **v2-typescript-safe-05**: Scan did not complete successfully; audit-store.ts: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-typescript-safe-06**: Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage; smtp-greeting.ts: no complete trusted-parser/check outcome
- **v2-typescript-vulnerable-01**: Scan did not complete successfully; print.ts: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage; settings.ts: no complete trusted-parser/check outcome
- **v2-typescript-vulnerable-02**: Scan did not complete successfully; mail-digest.ts: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage; subscription.ts: no complete trusted-parser/check outcome
- **v2-typescript-vulnerable-03**: Scan did not complete successfully; open-graph.ts: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-typescript-vulnerable-04**: Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage; transform.ts: no complete trusted-parser/check outcome
- **v2-typescript-vulnerable-05**: Scan did not complete successfully; case-list.ts: no complete trusted-parser/check outcome; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage
- **v2-typescript-vulnerable-06**: Scan did not complete successfully; semgrep: applicable scanner did not complete; semgrep: incomplete scanner coverage; token-client.ts: no complete trusted-parser/check outcome

A missed expected finding is a detection observation, not permission to relabel or tune a held-out case. Unexpected findings require independent semantic review. Parse/check failures stay incomplete; they must not count as safe results. The full journal retains source/specification hashes, exact reports, tool coverage and prior attempts.
