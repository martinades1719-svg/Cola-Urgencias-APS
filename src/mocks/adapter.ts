import {
  alerts,
  auditLogs,
  demoUsers,
  episodes,
} from './data';

import {
  canAssess,
  canAudit,
  canManageUsers,
  canOperate,
  estimateWait,
  randomTicket,
  sortQueue,
  validateAssessment,
} from '@/utils/clinical';

import type {
  ArrivalInput,
  AssessmentInput,
  AuthSession,
  DashboardMetrics,
  Episode,
  EpisodeStatus,
  PublicStatus,
  Role,
  User,
} from '@/types';


let session: AuthSession | null = null;
let threshold = 60;


const now = (): string =>
  new Date().toISOString();


const snapshot = <T,>(
  data: T,
): T => structuredClone(data);


function requireUser(): User {
  if (
    !session ||
    !session.user.active
  ) {
    throw new Error(
      'Inicia sesión para continuar.',
    );
  }

  return session.user;
}


function requireQueue(): User {
  const user = requireUser();

  if (user.role === 'ADMIN') {
    throw new Error(
      'Acceso denegado.',
    );
  }

  return user;
}


function findEpisode(
  id: string,
): Episode {
  const episode = episodes.find(
    (item) => item.id === id,
  );

  if (!episode) {
    throw new Error(
      'No encontramos el episodio.',
    );
  }

  return episode;
}


function audit(
  user: User,
  episode: Episode,
  action: string,
  previous: string,
  next: string,
): void {
  auditLogs.unshift({
    id: crypto.randomUUID(),
    createdAt: now(),
    user: user.email,
    role: user.role,
    action,
    entity: 'Episodio',
    ticket: episode.ticket,
    previous,
    next,
    result: 'Completado',
  });
}


function position(
  episode: Episode,
) {
  const queue = sortQueue(episodes);

  const index = queue.findIndex(
    (item) => item.id === episode.id,
  );

  return {
    approximate:
      index >= 0
        ? index + 1
        : null,

    estimate: estimateWait(
      episode,
      queue,
    ),

    reordered:
      episode.status === 'WAITING' &&
      queue.some(
        (item) =>
          Date.parse(item.arrivedAt) >
            Date.parse(episode.arrivedAt) &&
          (item.priority ?? 'C5') <
            (episode.priority ?? 'C5'),
      ),
  };
}


export const mockApi = {
  /**
   * Permite que la autenticación real de FastAPI comparta
   * temporalmente el usuario con los módulos que aún usan mocks.
   */
  async setAuthenticatedUser(
    user: User,
  ): Promise<void> {
    session = {
      user,
      accessToken: 'hybrid-session',
    };
  },


  async login(
    email: string,
    password: string,
  ): Promise<AuthSession> {
    const normalizedEmail = email
      .toLowerCase()
      .trim();

    const user = demoUsers.find(
      (item) =>
        item.email === normalizedEmail &&
        item.active,
    );

    if (
      !user ||
      password !== 'Demo_2026!Seguro'
    ) {
      throw new Error(
        'Correo o contraseña incorrectos.',
      );
    }

    session = {
      user,
      accessToken: 'mock-session',
      refreshToken: 'mock-refresh',
    };

    return session;
  },


  async restore(): Promise<AuthSession | null> {
    if (typeof window === 'undefined') {
      return null;
    }

    const email = sessionStorage.getItem(
      'aps-demo-email',
    );

    const user = demoUsers.find(
      (item) =>
        item.email === email &&
        item.active,
    );

    session = user
      ? {
          user,
          accessToken: 'mock-session',
          refreshToken: 'mock-refresh',
        }
      : null;

    return session;
  },


  async me(): Promise<User> {
    return requireUser();
  },


  async refresh(): Promise<AuthSession | null> {
    requireUser();
    return session;
  },


  async logout(): Promise<void> {
    session = null;
  },


  async arrival(
    input: ArrivalInput,
  ) {
    if (!input.privacy) {
      throw new Error(
        'Debes aceptar el aviso de privacidad.',
      );
    }

    const timestamp = now();

    const episode: Episode = {
      id: crypto.randomUUID(),
      ticket: randomTicket(),
      token: crypto.randomUUID(),

      patient: {
        id: crypto.randomUUID(),
        document: input.document,
        firstName: input.firstName,
        lastName: input.lastName,
        birthDate: input.birthDate,
      },

      status: 'PENDING_TRIAGE',
      priority: null,
      arrivedAt: timestamp,
      updatedAt: timestamp,
      triageAt: null,
      calledAt: null,
      box: null,
      assessments: [],
      reassessments: [],
      closureReason: null,
      closedAt: null,
      closedBy: null,
    };

    episodes.unshift(episode);

    auditLogs.unshift({
      id: crypto.randomUUID(),
      createdAt: timestamp,
      user: 'Registro público',
      role: 'RECEPTION',
      action: 'Llegada registrada',
      entity: 'Episodio',
      ticket: episode.ticket,
      previous: '—',
      next: 'PENDING_TRIAGE',
      result: 'Completado',
    });

    return {
      ticket: episode.ticket,
      token: episode.token,
      arrivedAt: episode.arrivedAt,
    };
  },


  async publicStatus(
    token: string,
  ): Promise<PublicStatus> {
    const normalizedToken = token
      .toUpperCase()
      .trim();

    const episode = episodes.find(
      (item) =>
        item.token === token ||
        item.ticket.toUpperCase() ===
          normalizedToken,
    );

    if (!episode) {
      throw new Error(
        'No encontramos ese ticket. Revisa el código e inténtalo nuevamente.',
      );
    }

    return {
      ticket: episode.ticket,
      status: episode.status,
      arrivedAt: episode.arrivedAt,
      updatedAt: episode.updatedAt,
      box: episode.box,
      position: position(episode),
    };
  },


  async episodes(): Promise<Episode[]> {
    requireQueue();
    return snapshot(episodes);
  },


  async episode(
    id: string,
  ): Promise<Episode> {
    requireQueue();
    return snapshot(
      findEpisode(id),
    );
  },


  async pending(): Promise<Episode[]> {
    requireQueue();

    return snapshot(
      episodes.filter(
        (episode) =>
          episode.status ===
          'PENDING_TRIAGE',
      ),
    );
  },


  async triage(
    id: string,
    input: AssessmentInput,
  ): Promise<Episode> {
    const user = requireUser();
    const episode = findEpisode(id);

    validateAssessment(
      user.role,
      null,
      input.priority,
      input.reason,
    );

    if (
      episode.status !==
      'PENDING_TRIAGE'
    ) {
      throw new Error(
        'Este episodio ya tiene un triage.',
      );
    }

    const createdAt = now();

    episode.assessments.push({
      id: crypto.randomUUID(),
      priority: input.priority,
      observation: input.observation,
      createdAt,
      userId: user.id,
    });

    episode.priority = input.priority;
    episode.triageAt = createdAt;
    episode.updatedAt = createdAt;
    episode.status = 'WAITING';

    audit(
      user,
      episode,
      'Triage inicial',
      'PENDING_TRIAGE',
      input.priority,
    );

    return episode;
  },


  async reassess(
    id: string,
    input: AssessmentInput,
  ): Promise<Episode> {
    const user = requireUser();
    const episode = findEpisode(id);

    validateAssessment(
      user.role,
      episode.priority,
      input.priority,
      input.reason,
    );

    if (
      !episode.priority ||
      ![
        'WAITING',
        'CALLED',
        'IN_CARE',
      ].includes(episode.status)
    ) {
      throw new Error(
        'Este episodio no admite reevaluaciones.',
      );
    }

    const previousPriority =
      episode.priority;

    const createdAt = now();

    const assessment = {
      id: crypto.randomUUID(),
      priority: input.priority,
      observation: input.observation,
      createdAt,
      userId: user.id,
    };

    episode.assessments.push(
      assessment,
    );

    episode.reassessments.push({
      ...assessment,
      previousPriority,
      reason: input.reason,
    });

    episode.priority = input.priority;
    episode.updatedAt = createdAt;

    audit(
      user,
      episode,
      'Reevaluación',
      previousPriority,
      input.priority,
    );

    return episode;
  },


  async transition(
    id: string,
    status: EpisodeStatus,
    value: string,
  ): Promise<Episode> {
    const user = requireQueue();

    if (!canOperate(user.role)) {
      throw new Error(
        'No tienes permiso para cambiar estados administrativos.',
      );
    }

    const episode = findEpisode(id);
    const previousStatus = episode.status;

    const invalidNormalTransition =
      (
        status === 'CALLED' &&
        previousStatus !== 'WAITING'
      ) ||
      (
        status === 'IN_CARE' &&
        previousStatus !== 'CALLED'
      ) ||
      (
        status === 'CLOSED' &&
        previousStatus !== 'IN_CARE'
      );

    if (invalidNormalTransition) {
      throw new Error(
        'El estado actual no permite esta acción.',
      );
    }

    if (
      status === 'WITHDRAWN' &&
      ![
        'PENDING_TRIAGE',
        'WAITING',
        'CALLED',
        'IN_CARE',
      ].includes(previousStatus)
    ) {
      throw new Error(
        'Este episodio ya está finalizado.',
      );
    }

    if (
      status === 'CALLED' &&
      !value.trim()
    ) {
      throw new Error(
        'Selecciona un box.',
      );
    }

    if (
      (
        status === 'CLOSED' ||
        status === 'WITHDRAWN'
      ) &&
      !value.trim()
    ) {
      throw new Error(
        'Selecciona el motivo del cierre.',
      );
    }

    episode.status = status;
    episode.updatedAt = now();

    if (status === 'CALLED') {
      episode.box = value;
      episode.calledAt = now();
    }

    if (
      status === 'CLOSED' ||
      status === 'WITHDRAWN'
    ) {
      episode.closureReason = value;
      episode.closedAt = now();
      episode.closedBy = user.id;
    }

    audit(
      user,
      episode,
      'Cambio de estado',
      previousStatus,
      `${status}${value ? ` · ${value}` : ''}`,
    );

    return episode;
  },


  async queue() {
    requireQueue();

    const queue = sortQueue(episodes);

    return queue.map(
      (episode, index) => ({
        ...episode,
        position: index + 1,

        estimate: estimateWait(
          episode,
          queue,
        ),

        hasAlert: alerts.some(
          (alert) =>
            alert.episodeId ===
              episode.id &&
            alert.status !== 'RESOLVED',
        ),
      }),
    );
  },


  async position(
    id: string,
  ) {
    requireQueue();

    return position(
      findEpisode(id),
    );
  },


  async alerts() {
    requireQueue();
    return snapshot(alerts);
  },


  async alertAction(
    id: string,
    action: 'take' | 'resolve',
  ) {
    const user = requireUser();

    if (!canAssess(user.role)) {
      throw new Error(
        'No tienes permisos para gestionar alertas.',
      );
    }

    const alert = alerts.find(
      (item) => item.id === id,
    );

    if (!alert) {
      throw new Error(
        'Alerta no encontrada.',
      );
    }

    if (
      alert.status === 'RESOLVED'
    ) {
      throw new Error(
        'La alerta ya fue resuelta.',
      );
    }

    alert.status =
      action === 'take'
        ? 'TAKEN'
        : 'RESOLVED';

    alert.takenBy = user.id;

    audit(
      user,
      findEpisode(alert.episodeId),
      action === 'take'
        ? 'Alerta tomada'
        : 'Alerta resuelta',
      'OPEN',
      alert.status,
    );

    return alert;
  },


  async dashboard(): Promise<DashboardMetrics> {
    requireQueue();

    return {
      pending: episodes.filter(
        (episode) =>
          episode.status ===
          'PENDING_TRIAGE',
      ).length,

      waiting: episodes.filter(
        (episode) =>
          episode.status ===
          'WAITING',
      ).length,

      called: episodes.filter(
        (episode) =>
          episode.status ===
          'CALLED',
      ).length,

      inCare: episodes.filter(
        (episode) =>
          episode.status ===
          'IN_CARE',
      ).length,

      alerts: alerts.filter(
        (alert) =>
          alert.status !== 'RESOLVED',
      ).length,

      averageWait: 38,
      registered: episodes.length,
      arrivalTriage: 14,
      triageCare: 38,

      reassessments: episodes.reduce(
        (total, episode) =>
          total +
          episode.reassessments.length,
        0,
      ),

      priorityChanges: episodes.reduce(
        (total, episode) =>
          total +
          episode.reassessments.filter(
            (assessment) =>
              assessment.previousPriority !==
              assessment.priority,
          ).length,
        0,
      ),

      resolvedAlerts: alerts.filter(
        (alert) =>
          alert.status === 'RESOLVED',
      ).length,

      withdrawals: episodes.filter(
        (episode) =>
          episode.status ===
          'WITHDRAWN',
      ).length,

      estimateAccuracy: 86,

      byPriority: (
        [
          'C1',
          'C2',
          'C3',
          'C4',
          'C5',
        ] as const
      ).map(
        (priority) => ({
          priority,
          count: episodes.filter(
            (episode) =>
              episode.priority ===
              priority,
          ).length,
        }),
      ),
    };
  },


  async audit() {
    const user = requireUser();

    if (!canAudit(user.role)) {
      throw new Error(
        'Acceso denegado.',
      );
    }

    return snapshot(auditLogs);
  },


  async users() {
    const user = requireUser();

    if (
      !canManageUsers(user.role)
    ) {
      throw new Error(
        'Acceso denegado.',
      );
    }

    return snapshot(demoUsers);
  },


  async createUser(
    input: {
      name?: string;
      email: string;
      role: Role;
    },
  ): Promise<User> {
    const actor = requireUser();

    if (
      !canManageUsers(actor.role)
    ) {
      throw new Error(
        'Acceso denegado.',
      );
    }

    const normalizedEmail =
      input.email
        .toLowerCase()
        .trim();

    if (
      demoUsers.some(
        (user) =>
          user.email.toLowerCase() ===
          normalizedEmail,
      )
    ) {
      throw new Error(
        'Este correo ya está registrado.',
      );
    }

    const user: User = {
      id: crypto.randomUUID(),
      name:
        input.name?.trim() ||
        'Usuario Demo',
      email: normalizedEmail,
      role: input.role,
      active: true,
    };

    demoUsers.push(user);

    auditLogs.unshift({
      id: crypto.randomUUID(),
      createdAt: now(),
      user: actor.email,
      role: actor.role,
      action: 'Usuario creado',
      entity: 'Usuario',
      ticket: '—',
      previous: '—',
      next: `${user.email} · ${user.role}`,
      result: 'Completado',
    });

    return user;
  },


  async userStatus(
    id: string,
    active: boolean,
  ): Promise<User> {
    const actor = requireUser();

    if (
      !canManageUsers(actor.role)
    ) {
      throw new Error(
        'Acceso denegado.',
      );
    }

    if (actor.id === id) {
      throw new Error(
        'No puedes desactivar tu propia cuenta.',
      );
    }

    const user = demoUsers.find(
      (item) => item.id === id,
    );

    if (!user) {
      throw new Error(
        'Usuario no encontrado.',
      );
    }

    user.active = active;

    auditLogs.unshift({
      id: crypto.randomUUID(),
      createdAt: now(),
      user: actor.email,
      role: actor.role,
      action: 'Estado de usuario',
      entity: 'Usuario',
      ticket: '—',
      previous: String(!active),
      next: String(active),
      result: 'Completado',
    });

    return user;
  },


  async threshold(
    value?: number,
  ): Promise<number> {
    const user = requireUser();

    if (
      user.role !==
      'CLINICAL_MANAGER'
    ) {
      throw new Error(
        'Acceso denegado.',
      );
    }

    if (value !== undefined) {
      if (
        value < 15 ||
        value > 240
      ) {
        throw new Error(
          'El umbral debe estar entre 15 y 240 minutos.',
        );
      }

      const previousThreshold =
        threshold;

      threshold = value;

      auditLogs.unshift({
        id: crypto.randomUUID(),
        createdAt: now(),
        user: user.email,
        role: user.role,
        action:
          'Umbral demostrativo actualizado',
        entity: 'Configuración',
        ticket: '—',
        previous: String(
          previousThreshold,
        ),
        next: String(value),
        result: 'Completado',
      });
    }

    return threshold;
  },
};