import React from "react";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import { HomeScreen } from "../features/home/HomeScreen";
import { FormatScreen } from "../features/formats/FormatScreen";
import { DownloadsScreen } from "../features/downloads/DownloadsScreen";

export type RootStackParamList = {
  Home: undefined;
  Format: undefined;
  Downloads: undefined;
};

const Stack = createNativeStackNavigator<RootStackParamList>();

export function AppNavigator() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerStyle: { backgroundColor: "#1a1a2e" },
        headerTintColor: "#eee",
        contentStyle: { backgroundColor: "#0f0f23" },
      }}
    >
      <Stack.Screen name="Home" component={HomeScreen} options={{ title: "YT Downloader" }} />
      <Stack.Screen name="Format" component={FormatScreen} options={{ title: "Select Quality" }} />
      <Stack.Screen name="Downloads" component={DownloadsScreen} options={{ title: "Downloads" }} />
    </Stack.Navigator>
  );
}
