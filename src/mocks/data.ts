import type {
  Alert,
  AuditLog,
  Episode,
  EpisodeStatus,
  Priority,
  User,
} from '@/types';


const ago = (minutes: number): string =>
  new Date(Date.now() - minutes * 60_000).toISOString();


export const demoUsers: User[] = [
  {
    id: 'u1',
    name: 'Recepción Demo',
    email: 'recepcion@demo.cl',
    role: 'RECEPTION',
    active: true,
  },
  {
    id: 'u2',
    name: 'Triage Demo',
    email: 'triage@demo.cl',
    role: 'TRIAGE',
    active: true,
  },
  {
    id: 'u3',
    name: 'Jefatura Demo',
    email: 'jefatura@demo.cl',
    role: 'CLINICAL_MANAGER',
    active: true,
  },
  {
    id: 'u4',
    name: 'Administrador Demo',
    email: 'admin@demo.cl',
    role: 'ADMIN',
    active: true,
  },
];


const names = [
  'Valentina',
  'Jorge',
  'Francisca',
  'Pedro',
  'Isabel',
  'Diego',
  'Antonia',
  'Carlos',
  'Sofía',
  'Tomás',
  'Elena',
  'Matías',
  'Paula',
  'Ignacio',
  'Laura',
  'Benjamín',
  'Ana',
  'Felipe',
];


const lastNames = [
  'González',
  'Pérez',
  'Muñoz',
  'Soto',
  'Rojas',
  'Díaz',
];


const tickets = [
  'A7K2P9',
  'M4R8T1',
  'B6N3W2',
  'H9D5L7',
  'F2X8Q4',
  'J3V6S9',
  'P8C4A2',
  'T5E9K3',
  'R1N7B6',
  'W6L2F8',
  'D4Q9M5',
  'X8A3V7',
  'K2S6H1',
  'N9P4J8',
  'E7T1R3',
  'L5B8C2',
  'Q3M7D9',
  'V8F2X6',
];


const priorities: Priority[] = [
  'C2',
  'C3',
  'C4',
  'C3',
  'C5',
  'C1',
  'C4',
  'C2',
  'C3',
  'C4',
  'C2',
  'C3',
  'C4',
  'C5',
];


export const episodes: Episode[] = names.map(
  (name, index) => {
    const status: EpisodeStatus =
      index < 4
        ? 'PENDING_TRIAGE'
        : index < 12
          ? 'WAITING'
          : index < 14
            ? 'CALLED'
            : index < 16
              ? 'IN_CARE'
              : 'CLOSED';

    const priority: Priority | null =
      index < 4
        ? null
        : priorities[index - 4] ?? 'C5';

    const arrivedAt = ago(12 + index * 8);

    const triageAt = priority
      ? ago(index === 9 ? 3 : 5 + (index - 4) * 7)
      : null;

    return {
      id: `e${index + 1}`,
      ticket: `URG-${tickets[index]}`,
      token: `demo-public-${tickets[index]}`,

      patient: {
        id: `p${index + 1}`,
        document: `DEMO-${index + 10_000}`,
        firstName: name,
        lastName: lastNames[index % lastNames.length] ?? 'Soto',
        birthDate: '1990-06-15',
      },

      status,
      priority,
      arrivedAt,
      updatedAt: triageAt ?? arrivedAt,
      triageAt,

      calledAt:
        status === 'CALLED'
          ? ago(8)
          : null,

      box:
        status === 'CALLED' || status === 'IN_CARE'
          ? `Box ${(index % 3) + 1}`
          : null,

      assessments: priority
        ? [
            {
              id: `t${index}`,
              priority,
              observation: 'Evaluación presencial registrada.',
              createdAt: triageAt ?? arrivedAt,
              userId: 'u2',
            },
          ]
        : [],

      reassessments:
        index === 7
          ? [
              {
                id: 'r1',
                priority: 'C3',
                previousPriority: 'C4',
                reason: 'Reevaluación presencial.',
                observation: 'Nueva evaluación registrada.',
                createdAt: ago(10),
                userId: 'u2',
              },
            ]
          : [],

      closureReason:
        status === 'CLOSED'
          ? 'Atención finalizada'
          : null,

      closedAt:
        status === 'CLOSED'
          ? ago(3)
          : null,

      closedBy:
        status === 'CLOSED'
          ? 'u1'
          : null,
    };
  },
);


export const alerts: Alert[] = [
  {
    id: 'a1',
    episodeId: 'e7',
    ticket: episodes[6]?.ticket ?? '',
    priority: 'C4',
    type: 'LONG_WAIT',
    status: 'OPEN',
    createdAt: ago(18),
    takenBy: null,
  },
  {
    id: 'a2',
    episodeId: 'e8',
    ticket: episodes[7]?.ticket ?? '',
    priority: 'C3',
    type: 'REASSESSMENT',
    status: 'OPEN',
    createdAt: ago(12),
    takenBy: null,
  },
  {
    id: 'a3',
    episodeId: 'e13',
    ticket: episodes[12]?.ticket ?? '',
    priority: 'C3',
    type: 'CALLED_DELAY',
    status: 'OPEN',
    createdAt: ago(8),
    takenBy: null,
  },
];


export const auditLogs: AuditLog[] = [
  {
    id: 'log1',
    createdAt: ago(10),
    user: 'Daniela Rojas',
    role: 'TRIAGE',
    action: 'Reevaluación de prioridad',
    entity: 'Episodio',
    ticket: episodes[7]?.ticket ?? '',
    previous: 'C4',
    next: 'C3',
    result: 'Completado',
  },

  ...episodes
    .filter((episode) => episode.priority)
    .slice(0, 6)
    .map(
      (episode, index): AuditLog => ({
        id: `log${index + 2}`,
        createdAt: episode.triageAt ?? episode.arrivedAt,
        user: 'Daniela Rojas',
        role: 'TRIAGE',
        action: 'Triage inicial',
        entity: 'Episodio',
        ticket: episode.ticket,
        previous: 'Pendiente de triage',
        next: episode.priority ?? '',
        result: 'Completado',
      }),
    ),
];