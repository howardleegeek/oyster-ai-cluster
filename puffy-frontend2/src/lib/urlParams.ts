export const URL_PARAMS = {
  CAMPAIGN_ID: 'campaign_id',
  AUTH_CODE: 'auth_code',
  PROMOTION_ID: 'promotion_id',
} as const;

export type UrlParam = typeof URL_PARAMS[keyof typeof URL_PARAMS];