const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

const RAG_BASE_URL =
  process.env.NEXT_PUBLIC_RAG_API_URL || "http://127.0.0.1:8001";

const API_MODE = process.env.NEXT_PUBLIC_API_MODE || "real";

type SlotItem = {
  id: string;
  doctor_id: string;
  date: string;
  time: string;
  status: string;
};

type ReservePayload = {
  patient_id: string;
  slot_id: string;
};

async function safeJson(res: Response) {
  const text = await res.text();
  try {
    return JSON.parse(text);
  } catch {
    return text;
  }
}

async function fetchBackend(
  endpoint: string,
  options: RequestInit = {},
  useRag = false
) {
  const baseUrl = useRag ? RAG_BASE_URL : API_BASE_URL;

  const res = await fetch(`${baseUrl}${endpoint}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  const data = await safeJson(res);

  if (!res.ok) {
    throw new Error(
      typeof data === "string" ? data : JSON.stringify(data)
    );
  }

  return data;
}

const mockSlots: SlotItem[] = [
  { id: "ahmed_thursday_10:00 AM", doctor_id: "ahmed", date: "thursday", time: "10:00 AM", status: "available" },
  { id: "ahmed_thursday_2:00 PM", doctor_id: "ahmed", date: "thursday", time: "2:00 PM", status: "available" },
  { id: "ahmed_thursday_4:00 PM", doctor_id: "ahmed", date: "thursday", time: "4:00 PM", status: "available" },
  { id: "sara_thursday_9:00 AM", doctor_id: "sara", date: "thursday", time: "9:00 AM", status: "available" },
  { id: "sara_thursday_1:00 PM", doctor_id: "sara", date: "thursday", time: "1:00 PM", status: "available" },
  { id: "omar_friday_9:00 AM", doctor_id: "omar", date: "friday", time: "9:00 AM", status: "available" },
];

function normalizeSlotResponse(data: any): SlotItem[] {
  if (Array.isArray(data)) {
    return data;
  }

  if (data && Array.isArray(data.available_slots)) {
    return data.available_slots.map((time: string) => ({
      id: `${data.doctor_id}_${data.date}_${time}`,
      doctor_id: data.doctor_id,
      date: data.date,
      time,
      status: "available",
    }));
  }

  return [];
}

export const apiClient = {
  async getSlots(): Promise<SlotItem[]> {
    if (API_MODE === "mock") {
      return mockSlots;
    }

    const combinations = [
      { doctor_id: "ahmed", date: "thursday" },
      { doctor_id: "ahmed", date: "friday" },
      { doctor_id: "sara", date: "thursday" },
      { doctor_id: "sara", date: "friday" },
      { doctor_id: "omar", date: "thursday" },
      { doctor_id: "omar", date: "friday" },
    ];

    const results = await Promise.all(
      combinations.map(async ({ doctor_id, date }) => {
        try {
          const data = await fetchBackend(
            `/slots?doctor_id=${doctor_id}&date=${date}`
          );
          return normalizeSlotResponse(data);
        } catch {
          return [];
        }
      })
    );

    return results.flat();
  },

  async reserveSlot(payload: ReservePayload) {
    if (API_MODE === "mock") {
      return { success: true, message: "Mock reservation created" };
    }

    return fetchBackend("/reserve", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  },

  async getPatientHistory(patientId: string) {
    if (API_MODE === "mock") {
      return {
        patient_id: patientId,
        history: [],
      };
    }

    return fetchBackend(`/patient/${patientId}/history`);
  },

  async retrieveRag(query: string, n_results = 3) {
    return fetchBackend(
      "/retrieve",
      {
        method: "POST",
        body: JSON.stringify({ query, n_results }),
      },
      true
    );
  },
};