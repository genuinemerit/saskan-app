# GitHub Notes

## Using a Passkey with SSH

If encountering issues with your SSH connection to GitHub after enabling a passkey. Here are some steps to troubleshoot and resolve the issue:

### 1. **Check SSH Configuration**

Make sure your SSH configuration is still set up correctly. Verify that your `~/.ssh/config` file (if it exists) includes an entry for GitHub:

```plaintext
Host github.com
  User git
  IdentityFile ~/.ssh/id_rsa  # or your specific private key file
```

### 2. **Verify Your Public Key**

Double-check that your SSH public key is still correctly added to your GitHub account. You can verify this by going to **Settings > SSH and GPG keys** on GitHub and ensuring your public key is listed there.

### 3. **Test SSH Connection**

Run the following command to test your SSH connection to GitHub:

```bash
ssh -T git@github.com
```

If it’s set up correctly, you should see a message like:

```
Hi username! You've successfully authenticated, but GitHub does not provide shell access.
```

If you get an error or a timeout, there may be a network issue or a firewall blocking your connection.

### 4. **Network Configuration**

Since you mentioned a timeout, check if your network configuration has changed:

* **Firewall Settings**: Ensure that port 22 (used for SSH) is open in your firewall settings.
* **VPN/Proxy**: If you're using a VPN or proxy, try disconnecting from it and test again.

### 5. **Use HTTPS as a Workaround**

If you're unable to resolve the SSH issues, consider switching to HTTPS for pushing to your repository temporarily. You can change the remote URL using:

```bash
git remote set-url origin https://github.com/username/repository.git
```

### 6. **Revisit Passkey Configuration**

If the issue arose after setting up a passkey, ensure that the passkey configuration did not inadvertently alter your SSH settings.

### 7. **Regenerate SSH Keys**

As a last resort, you can regenerate your SSH keys:

```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

Then add the new public key to your GitHub account.

### Summary

1. Check SSH configuration and public key.
2. Test your SSH connection.
3. Verify network settings.
4. Temporarily switch to HTTPS if needed.
5. Consider regenerating your SSH keys.

By following these steps, you should be able to diagnose and resolve the SSH connection issue with GitHub. If the problem persists, please provide any error messages or additional context for further assistance.

It turned out that the problem was with Network Configuration. We had increased the Firewall Setting to "Maximum", which evidently blocked apps communicating on port 22 or using SSH (not sure which). As soon as I throttled it back down to "Medium" then the git command worked properly over ssh.




