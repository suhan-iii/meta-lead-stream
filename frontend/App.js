import React, { useEffect, useState } from 'react';
import { StyleSheet, Text, View, FlatList, SafeAreaView, StatusBar, Platform } from 'react-native';

export default function App() {
  const [leads, setLeads] = useState([]);
  const [status, setStatus] = useState('Connecting...');

  const BACKEND_HOST = Platform.OS === 'android' ? '10.0.2.2:8000' : 'localhost:8000';
  const WS_URL = `ws://${BACKEND_HOST}/ws`;
  const HTTP_URL = `http://${BACKEND_HOST}/leads`;

  useEffect(() => {
    
    fetch(HTTP_URL)
      .then((res) => res.json())
      .then((data) => setLeads(data))
      .catch((err) => console.log('Fetch error:', err));

    
    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      setStatus('Connected to Lead Stream');
      console.log('WebSocket Connected');
    };

    ws.onmessage = (e) => {
      const newLead = JSON.parse(e.data);
      console.log('New Lead Received:', newLead);
      setLeads((prevLeads) => [newLead, ...prevLeads]);
    };

    ws.onerror = () => setStatus('Connection Error');
    ws.onclose = () => setStatus('Disconnected');

    return () => ws.close();
  }, []);

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="dark-content" />
      <View style={styles.header}>
        <Text style={styles.title}>Meta Lead Ads Live Stream</Text>
        <Text style={styles.status}>Status: {status}</Text>
      </View>

      <FlatList
        data={leads}
        keyExtractor={(item, index) => item.lead_id || index.toString()}
        renderItem={({ item }) => (
          <View style={styles.card}>
            <Text style={styles.name}>{item.full_name || 'Anonymous Lead'}</Text>
            <Text style={styles.detail}>Email: {item.email || 'N/A'}</Text>
            <Text style={styles.detail}>Phone: {item.phone_number || 'N/A'}</Text>
            <Text style={styles.idText}>Lead ID: {item.lead_id}</Text>
          </View>
        )}
        ListEmptyComponent={
          <Text style={styles.empty}>No leads captured yet. Submit a test lead!</Text>
        }
      />
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f5f7', paddingTop: 30 },
  header: { padding: 16, backgroundColor: '#ffffff', borderBottomWidth: 1, borderColor: '#e5e5ea' },
  title: { fontSize: 20, fontWeight: 'bold', color: '#1c1c1e' },
  status: { fontSize: 13, color: '#34c759', marginTop: 4 },
  card: { backgroundColor: '#ffffff', padding: 16, marginHorizontal: 16, marginTop: 12, borderRadius: 8, elevation: 2 },
  name: { fontSize: 16, fontWeight: 'bold', color: '#007aff' },
  detail: { fontSize: 14, color: '#3a3a3c', marginTop: 2 },
  idText: { fontSize: 11, color: '#8e8e93', marginTop: 6 },
  empty: { textAlign: 'center', marginTop: 40, color: '#8e8e93' }
});