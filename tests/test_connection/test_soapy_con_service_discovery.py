"""Unit tests for service discovery SOAP client."""

from py_altium365.connection.soapy_con_service_discovery import (
    ServiceEndpoints,
    SoapEndPointInfo,
    SoapServiceDiscoveryLoginResult,
    SoapServiceDiscoveryLoginUserInfoResult,
    SoapServiceDiscoveryResponse,
    SoapyConServiceDiscovery,
)


def test_service_discovery_login_populates_endpoints(mocker):
    discovery = SoapyConServiceDiscovery("https://workspace.example")
    user_info = SoapServiceDiscoveryLoginUserInfoResult(
        session_id="sess",
        user_id="u1",
        account_id="a1",
        email="u@example.com",
        user_name="user",
        first_name="U",
        last_name="Ser",
        organisation="Org",
        auth_type=1,
    )
    login_result = SoapServiceDiscoveryLoginResult(
        endpoints=[
            SoapEndPointInfo(service_kind="SEARCHBASE", service_url="https://search"),
            SoapEndPointInfo(service_kind="VAULT", service_url="https://vault"),
        ],
        user_info=user_info,
    )
    response = SoapServiceDiscoveryResponse(login_result=login_result)
    mocker.patch.object(discovery, "_send_command", return_value=response)

    assert discovery.login("user", "pass") is True
    assert discovery.user_info.session_id == "sess"
    assert discovery.service_urls.SEARCHBASE == "https://search"
    assert discovery.service_urls.VAULT == "https://vault"


def test_service_discovery_login_failure(mocker):
    discovery = SoapyConServiceDiscovery("https://workspace.example")
    response = mocker.Mock()
    response.login_result = None
    mocker.patch.object(discovery, "_send_command", return_value=response)

    assert discovery.login("user", "pass") is False
    assert discovery.user_info is None


def test_service_endpoints_model():
    endpoints = ServiceEndpoints(SEARCHBASE="https://search")
    assert endpoints.model_dump()["SEARCHBASE"] == "https://search"
