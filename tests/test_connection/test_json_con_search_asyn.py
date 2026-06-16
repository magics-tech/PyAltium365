import datetime
from typing import Union, Any

import pytest

from py_altium365.connection.json_con_search_async import (
    JsonConSearchAsync,
    JsonFacetedCounter,
    FacedType,
    SearchDataType,
    JsonDocument,
    JsonField,
    SearchDataBase,
)


def create_search_api(mocker) -> Union[JsonConSearchAsync, Any]:
    altium_workspace = mocker.Mock()
    url = "test_url"
    session_guid = "test_session_guid"
    host = "test_host"

    mocker.patch.object(
        JsonConSearchAsync,
        "_update_search_names_and_counters",
        new=mocker.AsyncMock(return_value=None),
    )

    return JsonConSearchAsync(altium_workspace, url, session_guid, host), altium_workspace


def test_init(mocker):
    altium_workspace = mocker.Mock()
    url = "test_url"
    session_guid = "test_session_guid"
    host = "test_host"

    mocker.patch.object(
        JsonConSearchAsync,
        "_update_search_names_and_counters",
        new=mocker.AsyncMock(return_value=None),
    )

    search = JsonConSearchAsync(altium_workspace, url, session_guid, host)
    assert search._url == url + "/v1.0/searchasync"
    assert search._altium_workspace == altium_workspace
    assert search._counters_up_to_date is False
    assert len(search._search_parameters) == 0
    assert len(search._search_counters) == 0
    assert search._total_hits == 0
    assert search._session_guid == session_guid
    assert search._host == host


@pytest.mark.anyio
async def test_add_search_parameter_new(mocker):
    search, _ = create_search_api(mocker)

    search._search_counters.append(JsonFacetedCounter(FacetName="test_name", faced_type=FacedType.NO_TYPE, TotalHitCount=0, Counters=[]))

    assert await search.add_search_parameter("test_name", "test_value") is True
    assert len(search._search_parameters) == 1
    assert search._search_parameters[0].item.term.field == "test_5FnameDD420E8DDD8B445E911A0601BB2B6D53"
    assert search._search_parameters[0].item.term.value == "test_value"


@pytest.mark.anyio
async def test_add_search_parameter_existing(mocker):
    search, _ = create_search_api(mocker)

    search._search_counters.append(JsonFacetedCounter(FacetName="test_name", faced_type=FacedType.NO_TYPE, TotalHitCount=0, Counters=[]))
    await search.add_search_parameter("test_name", "first_value")
    await search.add_search_parameter("test_name", "second_value")

    assert await search.add_search_parameter("test_name", "test_value") is True
    assert len(search._search_parameters) == 1
    assert len(search._search_parameters[0].item.items) == 3
    assert search._search_parameters[0].item.items[0].item.term.value == "test_value"
    assert search._search_parameters[0].item.items[1].item.term.value == "second_value"
    assert search._search_parameters[0].item.items[2].item.term.value == "first_value"


@pytest.mark.anyio
async def test_add_search_parameter_existing_with_other_name(mocker):
    search, _ = create_search_api(mocker)

    search._search_counters.append(JsonFacetedCounter(FacetName="test_name", faced_type=FacedType.NO_TYPE, TotalHitCount=0, Counters=[]))
    search._search_counters.append(JsonFacetedCounter(FacetName="test_name2", faced_type=FacedType.NO_TYPE, TotalHitCount=0, Counters=[]))
    await search.add_search_parameter("test_name", "first_value")
    await search.add_search_parameter("test_name", "second_value")

    assert await search.add_search_parameter("test_name2", "test_value") is True
    assert len(search._search_parameters) == 2
    assert len(search._search_parameters[0].item.items) == 2
    assert search._search_parameters[1].item.term.value == "test_value"
    assert search._search_parameters[0].item.items[0].item.term.value == "second_value"
    assert search._search_parameters[0].item.items[1].item.term.value == "first_value"


@pytest.mark.anyio
async def test_add_search_parameter_existing_force_remove(mocker):
    search, _ = create_search_api(mocker)

    search._search_counters.append(JsonFacetedCounter(FacetName="test_name", faced_type=FacedType.NO_TYPE, TotalHitCount=0, Counters=[]))
    await search.add_search_parameter("test_name", "first_value")

    assert await search.add_search_parameter("test_name", "test_value", remove_old=True) is True
    assert len(search._search_parameters) == 1
    assert search._search_parameters[0].item.term.value == "test_value"


@pytest.mark.anyio
async def test_add_search_parameter_no_counter(mocker):
    search, _ = create_search_api(mocker)

    assert await search.add_search_parameter("test_name", "test_value") is False
    assert len(search._search_parameters) == 0


@pytest.mark.anyio
async def test_remove_search_parameter(mocker):
    search, _ = create_search_api(mocker)

    search._search_counters.append(JsonFacetedCounter(FacetName="test_name", faced_type=FacedType.NO_TYPE, TotalHitCount=0, Counters=[]))
    await search.add_search_parameter("test_name", "first_value")
    await search.add_search_parameter("test_name", "second_value")

    assert await search.remove_search_parameter("test_name", "first_value") is True
    assert len(search._search_parameters) == 1
    assert search._search_parameters[0].item.term.value == "second_value"


@pytest.mark.anyio
async def test_get_all_search_parameters(mocker):
    search, _ = create_search_api(mocker)

    search._search_counters.append(JsonFacetedCounter(FacetName="test_name", faced_type=FacedType.NO_TYPE, TotalHitCount=0, Counters=[]))
    search._search_counters.append(JsonFacetedCounter(FacetName="test_name2", faced_type=FacedType.NO_TYPE, TotalHitCount=0, Counters=[]))
    await search.add_search_parameter("test_name", "first_value")
    await search.add_search_parameter("test_name", "second_value")
    await search.add_search_parameter("test_name2", "third_value")

    assert search.get_all_search_parameters() == {"test_name": ["second_value", "first_value"], "test_name2": ["third_value"]}


@pytest.mark.anyio
async def test_clear_search_parameters(mocker):
    search, _ = create_search_api(mocker)

    search._search_counters.append(JsonFacetedCounter(FacetName="test_name", faced_type=FacedType.NO_TYPE, TotalHitCount=0, Counters=[]))
    search._search_counters.append(JsonFacetedCounter(FacetName="test_name2", faced_type=FacedType.NO_TYPE, TotalHitCount=0, Counters=[]))
    await search.add_search_parameter("test_name", "first_value")
    await search.add_search_parameter("test_name", "second_value")
    await search.add_search_parameter("test_name2", "third_value")

    search.clear_search_parameters()
    assert len(search._search_parameters) == 0


@pytest.mark.anyio
async def test_add_content_search_parameter(mocker):
    search, _ = create_search_api(mocker)

    search._search_counters.append(JsonFacetedCounter(FacetName="ContentType", faced_type=FacedType.NO_TYPE, TotalHitCount=0, Counters=[]))

    assert await search.add_content_search_parameter(SearchDataType.COMPONENT) is True
    assert len(search._search_parameters) == 1
    assert search._search_parameters[0].item.term.field == "ContentTypeDD420E8DDD8B445E911A0601BB2B6D53"
    assert search._search_parameters[0].item.term.value == "Component"


@pytest.mark.anyio
async def test_add_content_search_parameter_add(mocker):
    search, _ = create_search_api(mocker)

    search._search_counters.append(JsonFacetedCounter(FacetName="ContentType", faced_type=FacedType.NO_TYPE, TotalHitCount=0, Counters=[]))
    await search.add_content_search_parameter(SearchDataType.COMPONENT)

    assert await search.add_content_search_parameter(SearchDataType.DATASHEET) is True
    assert len(search._search_parameters) == 1
    assert search._search_parameters[0].item.items[0].item.term.value == "Datasheet"
    assert search._search_parameters[0].item.items[1].item.term.value == "Component"


@pytest.mark.anyio
async def test_remove_content_search_parameter(mocker):
    search, _ = create_search_api(mocker)

    search._search_counters.append(JsonFacetedCounter(FacetName="ContentType", faced_type=FacedType.NO_TYPE, TotalHitCount=0, Counters=[]))
    await search.add_content_search_parameter(SearchDataType.COMPONENT)

    assert await search.remove_content_search_parameter(SearchDataType.COMPONENT) is True
    assert len(search._search_parameters) == 0


@pytest.mark.anyio
async def test_add_search_parameter_range(mocker):
    search, _ = create_search_api(mocker)

    search._search_counters.append(JsonFacetedCounter(FacetName="test_name", faced_type=FacedType.NO_TYPE, TotalHitCount=0, Counters=[], SupportRange=True))

    assert await search.add_search_parameter_range("test_name", 2.0, 4.0) is True
    assert len(search._search_parameters) == 1
    assert search._search_parameters[0].item.field == "test_5FnameDD420E8DDD8B445E911A0601BB2B6D53"
    assert search._search_parameters[0].item.min == 2.0
    assert search._search_parameters[0].item.max == 4.0
    assert search._search_parameters[0].item.min_inclusive is True
    assert search._search_parameters[0].item.max_inclusive is True


@pytest.mark.anyio
async def test_add_search_parameter_range_no_counter(mocker):
    search, _ = create_search_api(mocker)

    assert await search.add_search_parameter_range("test_name", 2.0, 4.0) is False
    assert len(search._search_parameters) == 0


@pytest.mark.anyio
async def test_add_search_parameter_range_no_support(mocker):
    search, _ = create_search_api(mocker)

    search._search_counters.append(JsonFacetedCounter(FacetName="test_name", faced_type=FacedType.NO_TYPE, TotalHitCount=0, Counters=[], SupportRange=False))

    assert await search.add_search_parameter_range("test_name", 2.0, 4.0) is False
    assert len(search._search_parameters) == 0


@pytest.mark.anyio
async def test_remove_search_parameter_range(mocker):
    search, _ = create_search_api(mocker)

    search._search_counters.append(JsonFacetedCounter(FacetName="test_name", faced_type=FacedType.NO_TYPE, TotalHitCount=0, Counters=[], SupportRange=True))
    await search.add_search_parameter_range("test_name", 2.0, 4.0)

    assert await search.remove_search_parameter_range("test_name") is True
    assert len(search._search_parameters) == 0


@pytest.mark.anyio
async def test_get_search_parameter_range(mocker):
    search, _ = create_search_api(mocker)

    search._search_counters.append(JsonFacetedCounter(FacetName="test_name", faced_type=FacedType.NO_TYPE, TotalHitCount=0, Counters=[], SupportRange=True))
    await search.add_search_parameter_range("test_name", 2.0, 4.0)

    assert await search.get_search_parameter_range("test_name") == (2.0, 4.0, True, True)


@pytest.mark.anyio
async def test_get_search_parameter_range_not_found(mocker):
    search, _ = create_search_api(mocker)

    assert await search.get_search_parameter_range("test_name") is None


@pytest.mark.anyio
async def test_get_all_search_parameters_range(mocker):
    search, _ = create_search_api(mocker)

    search._search_counters.append(JsonFacetedCounter(FacetName="test_name", faced_type=FacedType.NO_TYPE, TotalHitCount=0, Counters=[], SupportRange=True))
    search._search_counters.append(JsonFacetedCounter(FacetName="test_name2", faced_type=FacedType.NO_TYPE, TotalHitCount=0, Counters=[], SupportRange=True))
    await search.add_search_parameter_range("test_name", 2.0, 4.0)
    await search.add_search_parameter_range("test_name2", 3.0, 5.0)

    assert search.get_all_search_parameters_range() == {"test_name": (2.0, 4.0, True, True), "test_name2": (3.0, 5.0, True, True)}


@pytest.mark.anyio
async def test_clear_search_parameters_range(mocker):
    search, _ = create_search_api(mocker)

    search._search_counters.append(JsonFacetedCounter(FacetName="test_name", faced_type=FacedType.NO_TYPE, TotalHitCount=0, Counters=[], SupportRange=True))
    search._search_counters.append(JsonFacetedCounter(FacetName="test_name2", faced_type=FacedType.NO_TYPE, TotalHitCount=0, Counters=[], SupportRange=True))
    await search.add_search_parameter_range("test_name", 2.0, 4.0)
    await search.add_search_parameter_range("test_name2", 3.0, 5.0)

    search.clear_search_parameters_range()
    assert len(search._search_parameters) == 0


def test_add_search_parameter_wildcard(mocker):
    search, _ = create_search_api(mocker)

    assert search.add_search_parameter_wildcard("test_name") is True
    assert len(search._search_parameters) == 1
    assert search._search_parameters[0].item.items[0].item.term.field == "TextC623975962814A5FAAD7FA1CD85DA0DB"
    assert search._search_parameters[0].item.items[0].item.term.value == "test_name"
    assert search._search_parameters[0].item.items[1].item.term.field == "DynamicDataC623975962814A5FAAD7FA1CD85DA0DB"
    assert search._search_parameters[0].item.items[1].item.term.value == "test_name"


def test_add_search_parameter_wildcard_overwrite(mocker):
    search, _ = create_search_api(mocker)

    search.add_search_parameter_wildcard("test_name")
    assert search.add_search_parameter_wildcard("test_name2") is True
    assert len(search._search_parameters) == 1
    assert search._search_parameters[0].item.items[0].item.term.value == "test_name2"
    assert search._search_parameters[0].item.items[1].item.term.value == "test_name2"


def test_get_search_parameter_wildcard(mocker):
    search, _ = create_search_api(mocker)

    search.add_search_parameter_wildcard("test_name")
    assert search.get_search_parameter_wildcard() == "test_name"


def test_get_search_parameter_wildcard_not_found(mocker):
    search, _ = create_search_api(mocker)

    assert search.get_search_parameter_wildcard() is None


def test_get_current_count(mocker):
    search, _ = create_search_api(mocker)

    search._total_hits = 10
    search._counters_up_to_date = True  # skip network call
    assert search._total_hits == 10


@pytest.mark.anyio
async def test_get_all_search_names_and_type(mocker):
    search, _ = create_search_api(mocker)

    search._search_counters.append(JsonFacetedCounter(FacetName="test_name", faced_type=FacedType.NO_TYPE, TotalHitCount=0, Counters=[]))
    search._search_counters.append(JsonFacetedCounter(FacetName="test_name2", faced_type=FacedType.NO_TYPE, TotalHitCount=0, Counters=[]))

    assert await search.get_all_search_names_and_type() == [("test_name", FacedType.NO_TYPE), ("test_name2", FacedType.NO_TYPE)]


@pytest.mark.anyio
async def test_get_all_search_names(mocker):
    search, _ = create_search_api(mocker)

    search._search_counters.append(JsonFacetedCounter(FacetName="test_name", faced_type=FacedType.NO_TYPE, TotalHitCount=0, Counters=[]))
    search._search_counters.append(JsonFacetedCounter(FacetName="test_name2", faced_type=FacedType.NO_TYPE, TotalHitCount=0, Counters=[]))

    assert await search.get_all_search_names() == ["test_name", "test_name2"]


@pytest.mark.anyio
async def test_get_all_search_names_range(mocker):
    search, _ = create_search_api(mocker)

    search._search_counters.append(JsonFacetedCounter(FacetName="test_name", faced_type=FacedType.NO_TYPE, TotalHitCount=0, Counters=[], SupportRange=True))
    search._search_counters.append(JsonFacetedCounter(FacetName="test_name2", faced_type=FacedType.NO_TYPE, TotalHitCount=0, Counters=[], SupportRange=True))

    assert await search.get_all_search_names() == ["test_name", "test_name2"]


@pytest.mark.anyio
async def test_get_all_search_names_and_type_range(mocker):
    search, _ = create_search_api(mocker)

    search._search_counters.append(JsonFacetedCounter(FacetName="test_name", faced_type=FacedType.NO_TYPE, TotalHitCount=0, Counters=[], SupportRange=True))
    search._search_counters.append(JsonFacetedCounter(FacetName="test_name2", faced_type=FacedType.NO_TYPE, TotalHitCount=0, Counters=[], SupportRange=True))

    assert await search.get_all_search_names_and_type_range() == [("test_name", FacedType.NO_TYPE), ("test_name2", FacedType.NO_TYPE)]


def test_add_sort_field(mocker):
    search, _ = create_search_api(mocker)

    search.add_sort_field("HRID", descending=False)
    sort_fields = search.get_sort_fields()

    assert len(sort_fields) == 1
    assert sort_fields[0].name == "HRID"
    assert sort_fields[0].descending is False


def test_clear_sort_fields(mocker):
    search, _ = create_search_api(mocker)
    search.add_sort_field("HRID")

    search.clear_sort_fields()

    assert search.get_sort_fields() == []


@pytest.mark.anyio
async def test_get_results_page(mocker):
    search, altium_workspace = create_search_api(mocker)

    mock_result = mocker.Mock()
    mock_result.success = True
    mock_result.documents = [
        JsonDocument(
            Score=1.0,
            Fields=[JsonField(Name="HRID", Value="R-1"), JsonField(Name="CreatedAt", Value="0.41451")],
        )
    ]
    mocker.patch.object(search, "_send_command", new=mocker.AsyncMock(return_value=mock_result))

    page = await search.get_results_page(start=10, limit=5)

    assert len(page) == 1
    assert page[0].hrid == "R-1"
    request = search._send_command.call_args[0][0]
    assert request.start == 10
    assert request.limit == 5


@pytest.mark.anyio
async def test_get_results(mocker):
    search, altium_workspace = create_search_api(mocker)

    mock_result = mocker.Mock()
    mock_result.success = True
    mock_result.documents = [
        JsonDocument(
            Score=1.0,
            Fields=[
                JsonField(Name="test_name", Value="test_value"),
                JsonField(Name="test_name2", Value="test_value2"),
                JsonField(Name="CreatedAt", Value="0.41451"),
                JsonField(Name="LatestRevision", Value="0"),
            ],
        ),
        JsonDocument(
            Score=1.0,
            Fields=[
                JsonField(Name="test_name4", Value="test_value4"),
                JsonField(Name="test_name5", Value="test_value5"),
                JsonField(Name="CreatedAt", Value="5/5/2021 12:00:00"),
            ],
        ),
    ]
    mocker.patch.object(search, "_send_command", new=mocker.AsyncMock(return_value=mock_result))

    assert await search.get_results() == [
        SearchDataBase(
            altium_workspace=altium_workspace,
            Parameters={"test_name": "test_value", "test_name2": "test_value2"},
            CreatedAt=datetime.datetime(1899, 12, 31, 9, 56, 53, 664000),
            LatestRevision=False,
        ),
        SearchDataBase(
            altium_workspace=altium_workspace,
            Parameters={"test_name4": "test_value4", "test_name5": "test_value5"},
            CreatedAt=datetime.datetime(2021, 5, 5, 12, 0),
        ),
    ]
