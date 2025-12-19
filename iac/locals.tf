locals {
  # Parse the subscription id from env_variable.sh so runs don't require sourcing the file.
  env_file_content          = try(file("${path.module}/env_variable.sh"), "")
  subscription_line         = try(regex("ARM_SUBSCRIPTION_ID\\s*=\\s*\"[^\"]+\"", local.env_file_content), "")
  subscription_id_from_file = length(trimspace(local.subscription_line)) > 0 ? trimsuffix(trimprefix(trimspace(local.subscription_line), "ARM_SUBSCRIPTION_ID=\""), "\"") : null
    # COOP API key
  coop_api_key_line = try(
    regex("COOP_API_KEY\\s*=\\s*\"([^\"]+)\"", local.env_file_content),
    null
  )
  # Use the captured API key (index 1) rather than the entire match
  coop_api_key = local.coop_api_key_line != null ? local.coop_api_key_line[0] : null
}
