"""
Integration tests for Companies API CRUD workflow.

These tests use testcontainers to spin up a real PostgreSQL database
and test the complete workflow from API to database.

Author: Patryk Golabek
Copyright: 2025 Patryk Golabek
"""

import pytest
from fastapi import status
from fastapi.testclient import TestClient


@pytest.mark.integration
class TestCompaniesIntegration:
    """Integration tests for Companies CRUD workflow."""

    def test_create_read_update_delete_company_workflow(self, test_client: TestClient):
        """Test complete CRUD workflow for a company."""
        # 1. Create a company
        company_data = {
            "name": "Test Company Integration",
            "ir_url": "https://example.com/investor-relations",
            "primary_ticker": "TCI",
            "alternative_tickers": ["TCI.L", "TCI.US"],
        }

        # Create
        create_response = test_client.post("/api/v1/companies", json=company_data)
        assert create_response.status_code == status.HTTP_201_CREATED
        created_company = create_response.json()

        # Verify creation
        assert created_company["name"] == company_data["name"]
        assert created_company["primary_ticker"] == company_data["primary_ticker"]
        assert created_company["ir_url"] == company_data["ir_url"]
        assert created_company["id"] is not None
        company_id = created_company["id"]

        # 2. Read the company by ID
        get_response = test_client.get(f"/api/v1/companies/{company_id}")
        assert get_response.status_code == status.HTTP_200_OK
        retrieved_company = get_response.json()
        assert retrieved_company["id"] == company_id
        assert retrieved_company["name"] == company_data["name"]

        # 3. Update the company
        update_data = {
            "name": "Updated Test Company Integration",
            "ir_url": "https://example.com/new-ir",
        }
        update_response = test_client.put(f"/api/v1/companies/{company_id}", json=update_data)
        assert update_response.status_code == status.HTTP_200_OK
        updated_company = update_response.json()
        assert updated_company["name"] == update_data["name"]
        assert updated_company["ir_url"] == update_data["ir_url"]

        # 4. List companies and verify it appears
        list_response = test_client.get("/api/v1/companies")
        assert list_response.status_code == status.HTTP_200_OK
        companies = list_response.json()
        assert isinstance(companies, list)
        assert any(c["id"] == company_id for c in companies)

        # 5. Delete the company
        delete_response = test_client.delete(f"/api/v1/companies/{company_id}")
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # 6. Verify deletion
        get_after_delete = test_client.get(f"/api/v1/companies/{company_id}")
        assert get_after_delete.status_code == status.HTTP_404_NOT_FOUND

    def test_list_companies_with_pagination(self, test_client: TestClient):
        """Test listing companies with pagination."""
        # Create multiple companies
        company_ids = []
        for i in range(5):
            company_data = {
                "name": f"Company {i}",
                "ir_url": f"https://example.com/ir-{i}",
                "primary_ticker": f"COMP{i}",
            }
            response = test_client.post("/api/v1/companies", json=company_data)
            assert response.status_code == status.HTTP_201_CREATED
            company_ids.append(response.json()["id"])

        # List with limit
        list_response = test_client.get("/api/v1/companies?limit=3")
        assert list_response.status_code == status.HTTP_200_OK
        data = list_response.json()
        assert isinstance(data, list)
        assert len(data) >= 1  # We created 5, but limit is 3

        # Clean up
        for company_id in company_ids:
            test_client.delete(f"/api/v1/companies/{company_id}")

    def test_get_company_by_ticker(self, test_client: TestClient):
        """Test getting company by ticker."""
        # Create company
        company_data = {
            "name": "Ticker Test Company",
            "ir_url": "https://example.com/ir",
            "primary_ticker": "TTC",
        }
        create_response = test_client.post("/api/v1/companies", json=company_data)
        company_id = create_response.json()["id"]

        # Get by ticker
        get_response = test_client.get("/api/v1/companies/ticker/TTC")
        assert get_response.status_code == status.HTTP_200_OK
        retrieved = get_response.json()
        assert retrieved["id"] == company_id
        assert retrieved["primary_ticker"] == "TTC"

        # Clean up
        test_client.delete(f"/api/v1/companies/{company_id}")

    def test_create_multiple_companies_success(self, test_client: TestClient):
        """Test that creating multiple companies succeeds."""
        # Create first company
        company1_data = {
            "name": "Company One",
            "ir_url": "https://example.com/ir1",
            "primary_ticker": "CMP1",
        }
        response1 = test_client.post("/api/v1/companies", json=company1_data)
        assert response1.status_code == status.HTTP_201_CREATED
        company1_id = response1.json()["id"]

        # Create second company
        company2_data = {
            "name": "Company Two",
            "ir_url": "https://example.com/ir2",
            "primary_ticker": "CMP2",
        }
        response2 = test_client.post("/api/v1/companies", json=company2_data)
        assert response2.status_code == status.HTTP_201_CREATED
        company2_id = response2.json()["id"]

        # Verify both exist
        assert company1_id != company2_id

        # Clean up
        test_client.delete(f"/api/v1/companies/{company1_id}")
        test_client.delete(f"/api/v1/companies/{company2_id}")
