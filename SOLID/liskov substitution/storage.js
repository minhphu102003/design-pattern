// VIOLATION

class Storage {
  async save(key, bytes) {
    // contract: save succeeds or throws only on real I/O failure
    return { key };
  }

  getUrl(key) {
    return `https://cdn.example.com/${key}`;
  }
}

class ReadOnlyStorage extends Storage {
  async save(key, bytes) {
    // LSP violation: strengthens precondition ("must be writable")
    // Client code using Storage doesn't expect "read-only" to exist.
    throw new Error("Read-only storage: cannot save");
  }
}

async function uploadAvatar(storage, userId, bytes) {
  // Client expects ANY Storage works here.
  const key = `avatars/${userId}.png`;
  const saved = await storage.save(key, bytes);
  return storage.getUrl(saved.key);
}


(async () => {
  const writable = new Storage();
  console.log(await uploadAvatar(writable, "u1", Buffer.from("x"))); // OK

  const ro = new ReadOnlyStorage();
  console.log(await uploadAvatar(ro, "u1", Buffer.from("x"))); // BOOM
})();


class ReadableStorage {
  getUrl(key) {
    throw new Error("Not implemented!")
  }
}

class WriteableStorage extends ReadOnlyStorage {
  async save(key, bytes) {
    throw new Error("Not implemented!")
  }
}

class S3Storage extends WriteableStorage {
  async save(key, bytes) {
    return { key };
  }

  getUrl(key) {
    return `https://s3.amazonaws.com/${key}`;
  }
}

class CDNcache extends ReadableStorage {
  getUrl(key) {
    return `https://cdn.example.com/${key}`;
  }
}

async function uploadAvatar(storage, userId, bytes) {
  const key = `avatars/${userId}.png`;
  const saved = await storage.save(key, bytes);
  return storage.getUrl(saved.key);
}


