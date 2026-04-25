from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet


class ActionAskMissingInfo(Action):
    """Kiểm tra slot còn thiếu và hỏi đúng slot đó."""

    def name(self) -> Text:
        return "action_ask_missing_info"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        from_location = tracker.get_slot("from_location")
        to_location = tracker.get_slot("to_location")
        vehicle_type = tracker.get_slot("vehicle_type")

        if not from_location:
            dispatcher.utter_message(response="utter_ask_from_location")
        elif not to_location:
            dispatcher.utter_message(response="utter_ask_to_location")
        elif not vehicle_type:
            dispatcher.utter_message(response="utter_ask_vehicle_type")
        else:
            dispatcher.utter_message(response="utter_confirm_ride")

        return []


class ActionConfirmRide(Action):
    """Xác nhận chuyến đi khi đã đủ thông tin."""

    def name(self) -> Text:
        return "action_confirm_ride"

    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:

        from_location = tracker.get_slot("from_location")
        to_location = tracker.get_slot("to_location")
        vehicle_type = tracker.get_slot("vehicle_type")

        if from_location and to_location and vehicle_type:
            dispatcher.utter_message(
                text=f"✅ Đã đặt xe thành công!\n"
                     f"🚩 Điểm đi: {from_location}\n"
                     f"🏁 Điểm đến: {to_location}\n"
                     f"🚗 Loại xe: {vehicle_type}\n"
                     f"Vui lòng chờ tài xế đến đón bạn!"
            )
            # Reset slots sau khi đặt xong
            return [
                SlotSet("from_location", None),
                SlotSet("to_location", None),
                SlotSet("vehicle_type", None),
            ]
        else:
            dispatcher.utter_message(response="action_ask_missing_info")

        return []
