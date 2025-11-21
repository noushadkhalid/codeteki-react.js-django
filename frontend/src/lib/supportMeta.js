const DEFAULT_SUPPORT_META = {
  badge: "We respond within 24 hours",
  responseValue: "< 24 hrs",
  responseLabel: "Average response time",
  responseHelper: "Based on care plan",
  responseMessage: "Get a response within 24 hours",
  responseConfirmation: "We'll contact you within 24 hours to confirm your consultation.",
};

export function getSupportMeta(settings) {
  const support = settings?.support || {};
  return {
    badge: support.badge || DEFAULT_SUPPORT_META.badge,
    responseValue: support.responseValue || DEFAULT_SUPPORT_META.responseValue,
    responseLabel: support.responseLabel || DEFAULT_SUPPORT_META.responseLabel,
    responseHelper: support.responseHelper || DEFAULT_SUPPORT_META.responseHelper,
    responseMessage: support.responseMessage || DEFAULT_SUPPORT_META.responseMessage,
    responseConfirmation: support.responseConfirmation || DEFAULT_SUPPORT_META.responseConfirmation,
  };
}
