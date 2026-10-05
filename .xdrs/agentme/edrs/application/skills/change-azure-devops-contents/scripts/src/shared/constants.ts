// Azure DevOps' well-known, tenant-agnostic AAD resource id; always passed to `az rest`.
export const ADO_RESOURCE = '499b84ac-1321-427f-aa17-267ca6975798';
export const API_VERSION = '7.1';
// The work item comments API is still a preview in 7.1.
export const COMMENTS_API_VERSION = '7.1-preview.4';
export const THREAD_STATUSES = ['active', 'pending', 'fixed', 'wontFix', 'closed', 'byDesign'];
export const DEFAULT_BODY_FIELD = 'System.Description';
