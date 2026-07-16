"use client";

import { useMutation } from "@tanstack/react-query";

import { createLead } from "@/services/lead";
import type { LeadIntakePayload, LeadIntakeResult } from "@/types/domain";
import { ApiRequestError } from "@/types/api";

export function useSubmitLead() {
  return useMutation<LeadIntakeResult, ApiRequestError, LeadIntakePayload>({
    mutationFn: createLead,
  });
}
