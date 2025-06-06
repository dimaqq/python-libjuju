# DO NOT CHANGE THIS FILE! This file is auto-generated by facade.py.
# Changes will be overwritten/lost when the file is regenerated.

from juju.client._definitions import *
from juju.client.facade import ReturnMapping, Type


class AllModelWatcherFacade(Type):
    name = "AllModelWatcher"
    version = 4

    @ReturnMapping(AllWatcherNextResults)
    async def Next(self):
        """Next will return the current state of everything on the first call
        and subsequent calls will

        Returns -> AllWatcherNextResults
        """
        # map input types to rpc msg
        _params = dict()
        msg = dict(type="AllModelWatcher", request="Next", version=4, params=_params)

        reply = await self.rpc(msg)
        return reply

    @ReturnMapping(None)
    async def Stop(self):
        """Stop stops the watcher.

        Returns -> None
        """
        # map input types to rpc msg
        _params = dict()
        msg = dict(type="AllModelWatcher", request="Stop", version=4, params=_params)

        reply = await self.rpc(msg)
        return reply

    async def rpc(self, msg):
        """Patch rpc method to add Id."""
        if not hasattr(self, "Id"):
            raise RuntimeError('Missing "Id" field')
        msg["Id"] = id

        from .facade import TypeEncoder

        reply = await self.connection.rpc(msg, encoder=TypeEncoder)
        return reply


class ApplicationOffersFacade(Type):
    name = "ApplicationOffers"
    version = 4

    @ReturnMapping(ApplicationOffersResults)
    async def ApplicationOffers(self, bakery_version=None, offer_urls=None):
        """ApplicationOffers gets details about remote applications that match given URLs.

        bakery_version : int
        offer_urls : typing.Sequence[str]
        Returns -> ApplicationOffersResults
        """
        if bakery_version is not None and not isinstance(bakery_version, int):
            raise Exception(
                f"Expected bakery_version to be a int, received: {type(bakery_version)}"
            )

        if offer_urls is not None and not isinstance(offer_urls, (bytes, str, list)):
            raise Exception(
                f"Expected offer_urls to be a Sequence, received: {type(offer_urls)}"
            )

        # map input types to rpc msg
        _params = dict()
        msg = dict(
            type="ApplicationOffers",
            request="ApplicationOffers",
            version=4,
            params=_params,
        )
        _params["bakery-version"] = bakery_version
        _params["offer-urls"] = offer_urls
        reply = await self.rpc(msg)
        return reply

    @ReturnMapping(ErrorResults)
    async def DestroyOffers(self, force=None, offer_urls=None):
        """DestroyOffers removes the offers specified by the given URLs, forcing if necessary.

        force : bool
        offer_urls : typing.Sequence[str]
        Returns -> ErrorResults
        """
        if force is not None and not isinstance(force, bool):
            raise Exception(f"Expected force to be a bool, received: {type(force)}")

        if offer_urls is not None and not isinstance(offer_urls, (bytes, str, list)):
            raise Exception(
                f"Expected offer_urls to be a Sequence, received: {type(offer_urls)}"
            )

        # map input types to rpc msg
        _params = dict()
        msg = dict(
            type="ApplicationOffers", request="DestroyOffers", version=4, params=_params
        )
        _params["force"] = force
        _params["offer-urls"] = offer_urls
        reply = await self.rpc(msg)
        return reply

    @ReturnMapping(QueryApplicationOffersResults)
    async def FindApplicationOffers(self, filters=None):
        """FindApplicationOffers gets details about remote applications that match given filter.

        filters : typing.Sequence[~OfferFilter]
        Returns -> QueryApplicationOffersResults
        """
        if filters is not None and not isinstance(filters, (bytes, str, list)):
            raise Exception(
                f"Expected filters to be a Sequence, received: {type(filters)}"
            )

        # map input types to rpc msg
        _params = dict()
        msg = dict(
            type="ApplicationOffers",
            request="FindApplicationOffers",
            version=4,
            params=_params,
        )
        _params["Filters"] = filters
        reply = await self.rpc(msg)
        return reply

    @ReturnMapping(ConsumeOfferDetailsResults)
    async def GetConsumeDetails(self, offer_urls=None, user_tag=None):
        """GetConsumeDetails returns the details necessary to pass to another model
        to allow the specified args user to consume the offers represented by the args URLs.

        offer_urls : OfferURLs
        user_tag : str
        Returns -> ConsumeOfferDetailsResults
        """
        if offer_urls is not None and not isinstance(offer_urls, (dict, OfferURLs)):
            raise Exception(
                f"Expected offer_urls to be a OfferURLs, received: {type(offer_urls)}"
            )

        if user_tag is not None and not isinstance(user_tag, (bytes, str)):
            raise Exception(
                f"Expected user_tag to be a str, received: {type(user_tag)}"
            )

        # map input types to rpc msg
        _params = dict()
        msg = dict(
            type="ApplicationOffers",
            request="GetConsumeDetails",
            version=4,
            params=_params,
        )
        _params["offer-urls"] = offer_urls
        _params["user-tag"] = user_tag
        reply = await self.rpc(msg)
        return reply

    @ReturnMapping(QueryApplicationOffersResults)
    async def ListApplicationOffers(self, filters=None):
        """ListApplicationOffers gets deployed details about application offers that match given filter.
        The results contain details about the deployed applications such as connection count.

        filters : typing.Sequence[~OfferFilter]
        Returns -> QueryApplicationOffersResults
        """
        if filters is not None and not isinstance(filters, (bytes, str, list)):
            raise Exception(
                f"Expected filters to be a Sequence, received: {type(filters)}"
            )

        # map input types to rpc msg
        _params = dict()
        msg = dict(
            type="ApplicationOffers",
            request="ListApplicationOffers",
            version=4,
            params=_params,
        )
        _params["Filters"] = filters
        reply = await self.rpc(msg)
        return reply

    @ReturnMapping(ErrorResults)
    async def ModifyOfferAccess(self, changes=None):
        """ModifyOfferAccess changes the application offer access granted to users.

        changes : typing.Sequence[~ModifyOfferAccess]
        Returns -> ErrorResults
        """
        if changes is not None and not isinstance(changes, (bytes, str, list)):
            raise Exception(
                f"Expected changes to be a Sequence, received: {type(changes)}"
            )

        # map input types to rpc msg
        _params = dict()
        msg = dict(
            type="ApplicationOffers",
            request="ModifyOfferAccess",
            version=4,
            params=_params,
        )
        _params["changes"] = changes
        reply = await self.rpc(msg)
        return reply

    @ReturnMapping(ErrorResults)
    async def Offer(self, offers=None):
        """Offer makes application endpoints available for consumption at a specified URL.

        offers : typing.Sequence[~AddApplicationOffer]
        Returns -> ErrorResults
        """
        if offers is not None and not isinstance(offers, (bytes, str, list)):
            raise Exception(
                f"Expected offers to be a Sequence, received: {type(offers)}"
            )

        # map input types to rpc msg
        _params = dict()
        msg = dict(type="ApplicationOffers", request="Offer", version=4, params=_params)
        _params["Offers"] = offers
        reply = await self.rpc(msg)
        return reply

    @ReturnMapping(RemoteApplicationInfoResults)
    async def RemoteApplicationInfo(self, bakery_version=None, offer_urls=None):
        """RemoteApplicationInfo returns information about the requested remote application.
        This call currently has no client side API, only there for the Dashboard at this stage.

        bakery_version : int
        offer_urls : typing.Sequence[str]
        Returns -> RemoteApplicationInfoResults
        """
        if bakery_version is not None and not isinstance(bakery_version, int):
            raise Exception(
                f"Expected bakery_version to be a int, received: {type(bakery_version)}"
            )

        if offer_urls is not None and not isinstance(offer_urls, (bytes, str, list)):
            raise Exception(
                f"Expected offer_urls to be a Sequence, received: {type(offer_urls)}"
            )

        # map input types to rpc msg
        _params = dict()
        msg = dict(
            type="ApplicationOffers",
            request="RemoteApplicationInfo",
            version=4,
            params=_params,
        )
        _params["bakery-version"] = bakery_version
        _params["offer-urls"] = offer_urls
        reply = await self.rpc(msg)
        return reply


class ModelGenerationFacade(Type):
    name = "ModelGeneration"
    version = 4

    @ReturnMapping(ErrorResult)
    async def AbortBranch(self, branch=None):
        """AbortBranch aborts the input branch, marking it complete.  However no
        changes are made applicable to the whole model.  No units may be assigned
        to the branch when aborting.

        branch : str
        Returns -> ErrorResult
        """
        if branch is not None and not isinstance(branch, (bytes, str)):
            raise Exception(f"Expected branch to be a str, received: {type(branch)}")

        # map input types to rpc msg
        _params = dict()
        msg = dict(
            type="ModelGeneration", request="AbortBranch", version=4, params=_params
        )
        _params["branch"] = branch
        reply = await self.rpc(msg)
        return reply

    @ReturnMapping(ErrorResult)
    async def AddBranch(self, branch=None):
        """AddBranch adds a new branch with the input name to the model.

        branch : str
        Returns -> ErrorResult
        """
        if branch is not None and not isinstance(branch, (bytes, str)):
            raise Exception(f"Expected branch to be a str, received: {type(branch)}")

        # map input types to rpc msg
        _params = dict()
        msg = dict(
            type="ModelGeneration", request="AddBranch", version=4, params=_params
        )
        _params["branch"] = branch
        reply = await self.rpc(msg)
        return reply

    @ReturnMapping(BranchResults)
    async def BranchInfo(self, branches=None, detailed=None):
        """BranchInfo will return details of branch identified by the input argument,
        including units on the branch and the configuration disjoint with the
        master generation.
        An error is returned if no in-flight branch matching in input is found.

        branches : typing.Sequence[str]
        detailed : bool
        Returns -> BranchResults
        """
        if branches is not None and not isinstance(branches, (bytes, str, list)):
            raise Exception(
                f"Expected branches to be a Sequence, received: {type(branches)}"
            )

        if detailed is not None and not isinstance(detailed, bool):
            raise Exception(
                f"Expected detailed to be a bool, received: {type(detailed)}"
            )

        # map input types to rpc msg
        _params = dict()
        msg = dict(
            type="ModelGeneration", request="BranchInfo", version=4, params=_params
        )
        _params["branches"] = branches
        _params["detailed"] = detailed
        reply = await self.rpc(msg)
        return reply

    @ReturnMapping(IntResult)
    async def CommitBranch(self, branch=None):
        """CommitBranch commits the input branch, making its changes applicable to
        the whole model and marking it complete.

        branch : str
        Returns -> IntResult
        """
        if branch is not None and not isinstance(branch, (bytes, str)):
            raise Exception(f"Expected branch to be a str, received: {type(branch)}")

        # map input types to rpc msg
        _params = dict()
        msg = dict(
            type="ModelGeneration", request="CommitBranch", version=4, params=_params
        )
        _params["branch"] = branch
        reply = await self.rpc(msg)
        return reply

    @ReturnMapping(BoolResult)
    async def HasActiveBranch(self, branch=None):
        """HasActiveBranch returns a true result if the input model has an "in-flight"
        branch matching the input name.

        branch : str
        Returns -> BoolResult
        """
        if branch is not None and not isinstance(branch, (bytes, str)):
            raise Exception(f"Expected branch to be a str, received: {type(branch)}")

        # map input types to rpc msg
        _params = dict()
        msg = dict(
            type="ModelGeneration", request="HasActiveBranch", version=4, params=_params
        )
        _params["branch"] = branch
        reply = await self.rpc(msg)
        return reply

    @ReturnMapping(BranchResults)
    async def ListCommits(self):
        """ListCommits will return the commits, hence only branches with generation_id higher than 0

        Returns -> BranchResults
        """
        # map input types to rpc msg
        _params = dict()
        msg = dict(
            type="ModelGeneration", request="ListCommits", version=4, params=_params
        )

        reply = await self.rpc(msg)
        return reply

    @ReturnMapping(GenerationResult)
    async def ShowCommit(self, generation_id=None):
        """ShowCommit will return details a commit given by its generationId
        An error is returned if either no branch can be found corresponding to the generation id.
        Or the generation id given is below 1.

        generation_id : int
        Returns -> GenerationResult
        """
        if generation_id is not None and not isinstance(generation_id, int):
            raise Exception(
                f"Expected generation_id to be a int, received: {type(generation_id)}"
            )

        # map input types to rpc msg
        _params = dict()
        msg = dict(
            type="ModelGeneration", request="ShowCommit", version=4, params=_params
        )
        _params["generation-id"] = generation_id
        reply = await self.rpc(msg)
        return reply

    @ReturnMapping(ErrorResults)
    async def TrackBranch(self, branch=None, entities=None, num_units=None):
        """TrackBranch marks the input units and/or applications as tracking the input
        branch, causing them to realise changes made under that branch.

        branch : str
        entities : typing.Sequence[~Entity]
        num_units : int
        Returns -> ErrorResults
        """
        if branch is not None and not isinstance(branch, (bytes, str)):
            raise Exception(f"Expected branch to be a str, received: {type(branch)}")

        if entities is not None and not isinstance(entities, (bytes, str, list)):
            raise Exception(
                f"Expected entities to be a Sequence, received: {type(entities)}"
            )

        if num_units is not None and not isinstance(num_units, int):
            raise Exception(
                f"Expected num_units to be a int, received: {type(num_units)}"
            )

        # map input types to rpc msg
        _params = dict()
        msg = dict(
            type="ModelGeneration", request="TrackBranch", version=4, params=_params
        )
        _params["branch"] = branch
        _params["entities"] = entities
        _params["num-units"] = num_units
        reply = await self.rpc(msg)
        return reply


class SSHClientFacade(Type):
    name = "SSHClient"
    version = 4

    @ReturnMapping(SSHAddressesResults)
    async def AllAddresses(self, entities=None):
        """AllAddresses reports all addresses that might have SSH listening for each
        entity in args. The result is sorted with public addresses first.
        Machines and units are supported as entity types.

        entities : typing.Sequence[~Entity]
        Returns -> SSHAddressesResults
        """
        if entities is not None and not isinstance(entities, (bytes, str, list)):
            raise Exception(
                f"Expected entities to be a Sequence, received: {type(entities)}"
            )

        # map input types to rpc msg
        _params = dict()
        msg = dict(type="SSHClient", request="AllAddresses", version=4, params=_params)
        _params["entities"] = entities
        reply = await self.rpc(msg)
        return reply

    @ReturnMapping(CloudSpecResult)
    async def ModelCredentialForSSH(self):
        """ModelCredentialForSSH returns a cloud spec for ssh purpose.
        This facade call is only used for k8s model.

        Returns -> CloudSpecResult
        """
        # map input types to rpc msg
        _params = dict()
        msg = dict(
            type="SSHClient", request="ModelCredentialForSSH", version=4, params=_params
        )

        reply = await self.rpc(msg)
        return reply

    @ReturnMapping(SSHAddressResults)
    async def PrivateAddress(self, entities=None):
        """PrivateAddress reports the preferred private network address for one or
        more entities. Machines and units are supported.

        entities : typing.Sequence[~Entity]
        Returns -> SSHAddressResults
        """
        if entities is not None and not isinstance(entities, (bytes, str, list)):
            raise Exception(
                f"Expected entities to be a Sequence, received: {type(entities)}"
            )

        # map input types to rpc msg
        _params = dict()
        msg = dict(
            type="SSHClient", request="PrivateAddress", version=4, params=_params
        )
        _params["entities"] = entities
        reply = await self.rpc(msg)
        return reply

    @ReturnMapping(SSHProxyResult)
    async def Proxy(self):
        """Proxy returns whether SSH connections should be proxied through the
        controller hosts for the model associated with the API connection.

        Returns -> SSHProxyResult
        """
        # map input types to rpc msg
        _params = dict()
        msg = dict(type="SSHClient", request="Proxy", version=4, params=_params)

        reply = await self.rpc(msg)
        return reply

    @ReturnMapping(SSHAddressResults)
    async def PublicAddress(self, entities=None):
        """PublicAddress reports the preferred public network address for one
        or more entities. Machines and units are supported.

        entities : typing.Sequence[~Entity]
        Returns -> SSHAddressResults
        """
        if entities is not None and not isinstance(entities, (bytes, str, list)):
            raise Exception(
                f"Expected entities to be a Sequence, received: {type(entities)}"
            )

        # map input types to rpc msg
        _params = dict()
        msg = dict(type="SSHClient", request="PublicAddress", version=4, params=_params)
        _params["entities"] = entities
        reply = await self.rpc(msg)
        return reply

    @ReturnMapping(SSHPublicKeysResults)
    async def PublicKeys(self, entities=None):
        """PublicKeys returns the public SSH hosts for one or more
        entities. Machines and units are supported.

        entities : typing.Sequence[~Entity]
        Returns -> SSHPublicKeysResults
        """
        if entities is not None and not isinstance(entities, (bytes, str, list)):
            raise Exception(
                f"Expected entities to be a Sequence, received: {type(entities)}"
            )

        # map input types to rpc msg
        _params = dict()
        msg = dict(type="SSHClient", request="PublicKeys", version=4, params=_params)
        _params["entities"] = entities
        reply = await self.rpc(msg)
        return reply
