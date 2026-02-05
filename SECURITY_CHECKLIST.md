# Security Checklist for ASF-Engine

Use this checklist before deploying to production.

## ✅ Database Security

- [ ] Using PostgreSQL (not SQLite) in production
- [ ] Database password is strong (16+ characters)
- [ ] Database connection uses SSL/TLS
- [ ] Regular database backups configured
- [ ] Database user has minimal required permissions
- [ ] Connection pooling configured properly

## ✅ Authentication Security

- [ ] JWT_SECRET_KEY is 32+ characters
- [ ] JWT_SECRET_KEY is unique and randomly generated
- [ ] JWT_SECRET_KEY is not committed to git
- [ ] Session timeout configured (1 hour)
- [ ] Account lockout enabled (5 failed attempts)
- [ ] Password minimum length enforced (6+ characters)
- [ ] Passwords are bcrypt hashed (never plain text)

## ✅ Firebase Security (if using)

- [ ] Firebase API key is restricted to your domain
- [ ] Firebase authentication methods configured
- [ ] Firebase security rules are properly set
- [ ] Firebase credentials not in source control
- [ ] Firebase project has proper access controls

## ✅ Email Security

- [ ] SMTP credentials are secure (app password)
- [ ] Email account has 2FA enabled
- [ ] SMTP connection uses TLS
- [ ] Email sending limits monitored
- [ ] Email templates don't expose sensitive data

## ✅ Network Security

- [ ] Application runs on HTTPS (SSL/TLS)
- [ ] SSL certificates are valid and up to date
- [ ] CORS configured for specific domains only
- [ ] No wildcard CORS origins in production
- [ ] BASE_URL uses https:// in production

## ✅ Environment Variables

- [ ] .env file not committed to git
- [ ] All secrets are in environment variables
- [ ] Production .env different from development
- [ ] Environment variables documented in .env.example
- [ ] No hardcoded credentials in code

## ✅ Session Security

- [ ] Sessions expire after inactivity (1 hour)
- [ ] Session tokens are secure and unique
- [ ] Sessions stored securely in database
- [ ] Old sessions are cleaned up regularly
- [ ] Session hijacking protection enabled

## ✅ Input Validation

- [ ] Email format validation
- [ ] Password strength requirements
- [ ] SQL injection protection (using SQLAlchemy)
- [ ] XSS protection (Streamlit handles this)
- [ ] CSRF protection enabled

## ✅ Token Security

- [ ] JWT tokens have expiration (1 hour)
- [ ] Password reset tokens expire (1 hour)
- [ ] Email verification tokens expire (24 hours)
- [ ] Tokens are single-use
- [ ] Tokens are cryptographically secure

## ✅ Error Handling

- [ ] Errors don't expose system details
- [ ] Generic error messages for auth failures
- [ ] Logging doesn't include sensitive data
- [ ] Stack traces disabled in production
- [ ] Rate limiting on authentication endpoints

## ✅ Code Security

- [ ] No secrets in source code
- [ ] Dependencies are up to date
- [ ] No known vulnerabilities (run: pip audit)
- [ ] Input sanitization enabled
- [ ] SQL queries parameterized (SQLAlchemy)

## ✅ Deployment Security

- [ ] DEBUG=false in production
- [ ] ENVIRONMENT=production set
- [ ] Firewall configured properly
- [ ] Only necessary ports open
- [ ] Server access restricted
- [ ] Regular security updates applied

## ✅ Monitoring & Logging

- [ ] Failed login attempts logged
- [ ] Suspicious activity monitored
- [ ] Security events tracked
- [ ] Log rotation configured
- [ ] Logs don't contain passwords

## ✅ Backup & Recovery

- [ ] Database backups automated
- [ ] Backup restoration tested
- [ ] Backup encryption enabled
- [ ] Disaster recovery plan documented
- [ ] Recovery time objective (RTO) defined

## ✅ Compliance

- [ ] Privacy policy in place
- [ ] Terms of service available
- [ ] GDPR compliance (if applicable)
- [ ] Data retention policy defined
- [ ] User data deletion process

## ✅ Testing

- [ ] Authentication flow tested
- [ ] Password reset tested
- [ ] Email verification tested
- [ ] Role-based access tested
- [ ] Security vulnerabilities scanned

## Quick Security Commands

### Generate Secure JWT Secret
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### Check for Vulnerabilities
```bash
pip install pip-audit
pip-audit
```

### Test Password Strength
```python
from backend.auth import get_password_hash, verify_password
password = "test123"
hashed = get_password_hash(password)
print(f"Hash: {hashed[:50]}...")
print(f"Verify: {verify_password(password, hashed)}")
```

### Verify Database Connection
```bash
python -c "from backend.database import engine; print('Connected:', engine.connect())"
```

## Security Incident Response

If you discover a security issue:

1. **Do not** create a public GitHub issue
2. **Do** report privately to maintainers
3. **Include** reproduction steps
4. **Provide** impact assessment
5. **Wait** for response before disclosure

## Regular Security Maintenance

Schedule these tasks regularly:

### Weekly
- Review failed login attempts
- Check for suspicious activity
- Monitor email sending limits

### Monthly
- Update dependencies
- Review access logs
- Test backup restoration
- Scan for vulnerabilities

### Quarterly
- Security audit
- Penetration testing
- Review security policies
- Update security documentation

## Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [OWASP Cheat Sheets](https://cheatsheetseries.owasp.org/)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/14/faq/security.html)
- [JWT Best Practices](https://tools.ietf.org/html/rfc8725)

---

**Last Updated:** 2024
**Version:** 2.0.0
