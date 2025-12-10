package com.albertoroca.pupsdk.network

import java.net.InetAddress
import java.net.UnknownHostException
import okhttp3.Dns

/**
 * OkHttp [Dns] implementation that lets the SDK point specific hostnames to manual IP
 * addresses. This mirrors the behaviour of the Cloudflare/worker based backend where
 * some networks cannot resolve `*.workers.dev` domains.
 */
internal class ManualDns private constructor(
    private val overrides: Map<String, List<InetAddress>>
) : Dns {

    override fun lookup(hostname: String): List<InetAddress> {
        overrides[hostname]?.let { addresses ->
            if (addresses.isNotEmpty()) return addresses
        }
        return Dns.SYSTEM.lookup(hostname)
    }

    companion object {
        fun fromStrings(rawOverrides: Map<String, List<String>>): Dns? {
            if (rawOverrides.isEmpty()) return null

            val parsed = buildMap<String, List<InetAddress>> {
                rawOverrides.forEach { (host, ips) ->
                    val sanitizedHost = host.trim().lowercase()
                    val resolved = ips.mapNotNull { ip ->
                        val cleanIp = ip.trim()
                        if (cleanIp.isEmpty()) return@mapNotNull null
                        try {
                            InetAddress.getByName(cleanIp)
                        } catch (_: UnknownHostException) {
                            null
                        }
                    }
                    if (sanitizedHost.isNotEmpty() && resolved.isNotEmpty()) {
                        put(sanitizedHost, resolved)
                    }
                }
            }

            return if (parsed.isEmpty()) null else ManualDns(parsed)
        }
    }
}
